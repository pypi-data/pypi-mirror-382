# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import os.path
import sys
import stat
import functools
from typing import Any, Dict, Mapping, Optional
from platformdirs import user_config_dir, user_data_dir, user_cache_dir

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from kalle.domain.KalleConfig import KalleConfig, PromptsConfig

console_stderr = Console(file=sys.stderr)


def find_conversation_key(start_dir):
  path = start_dir or os.getcwd()
  expanded_path = os.path.expanduser(path)
  directories = expanded_path.split(os.path.sep)

  while len(directories) > 0:
    conversation_file = functools.reduce(lambda x, y: os.path.join(x, y), ["/", *directories, ".kalle_conversation"])
    if os.path.exists(conversation_file):
      with open(conversation_file) as f:
        return f.readline().strip()
    directories.pop()
  return None


def validate_config_permissions(config_file_path: str) -> bool:
  """Validate that the config file has appropriate permissions."""
  try:
    # Get the file's current permissions
    permissions = stat.S_IMODE(os.stat(config_file_path).st_mode)

    # Check if the permissions match 0600, otherwise bail as this file could contain secrets
    if permissions != 0o600:
      console_stderr.print(
          Panel(
              f"[bold]CONFIG LOCATION:[/bold] {config_file_path}\n"
              f"{Rule(style='red')}\n"
              f"The config file must have limited read access (0600), please update to be accessible only by your user and try again.",
              title="[red bold]CONFIGURATION PROBLEM",
              style="red",
          )
      )
      return False
    return True
  except Exception as e:
    console_stderr.print(f"[red]Error checking config file permissions: {e}")
    return False


class ConfigManager:

  def __init__(
      self,
      appname,
      appauthor,
      /,
      base_file_dir: str,
      conversation_key: Optional[str] = None,
      use_conversation_history: bool = True,
      use_memory: bool = False,
      format_output: Optional[bool] = None,
      config: Optional[Mapping] = None,
      debug: bool = False,
  ):
    self._appname = appname
    self._appauthor = appauthor
    self._conversation_key = conversation_key if use_conversation_history else None
    self._use_conversation_history = use_conversation_history
    self._use_memory = use_memory
    self._format_output = format_output
    self._debug = debug

    config_dir = user_config_dir(appname, appauthor)
    config_file_path = os.environ.get("KALLE_CONFIG") or f"{config_dir}/config.yml"

    self.kalle_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
    self._prompts = {}
    self._config = None

    # Ensure config dir exists
    os.makedirs(config_dir, exist_ok=True)

    # Ensure config file exists
    if not os.path.exists(config_file_path):
      import shutil

      os.makedirs(config_dir, exist_ok=True)
      shutil.copy(os.path.join(self.kalle_root, "kalle/data/config.yml.example"), config_file_path)
      os.chmod(config_file_path, 0o600)
      console_stderr.print(f"[orange1]Configuration file is missing {config_file_path}. [green]New config created.")

    # Validate permissions
    if not validate_config_permissions(config_file_path):
      sys.exit(112)
      return

    # Load configuration using pydantic_settings
    try:
      # Set the config file path in environment for pydantic_settings to pick up
      os.environ["KALLE_CONFIG"] = config_file_path
      if config is not None:
        self._config = KalleConfig(**config)
      else:
        self._config = KalleConfig()

      # Validate base profile exists
      if "base" not in self._config.profiles:
        console_stderr.print(
            Panel(
                f"[bold]CONFIG LOCATION:[/bold] {config_file_path}\n"
                f"{Rule(style='red')}\n"
                f"The 'base' profile must be configured.",
                title="[red bold]CONFIGURATION PROBLEM",
                style="red",
            )
        )
        sys.exit(110)
        return

      # Load prompt templates
      self.prompts = self._load_prompts(self._config.prompts)

      # Load patterns from files
      self.patterns = self._load_patterns(self._config.profiles)

      # Handle conversation key
      if use_conversation_history:
        if conversation_key is not None:
          return

        if self._config.default_conversation is not None and self._config.default_conversation != "":
          self._conversation_key = self._config.default_conversation

          return

        # Look for a configured file-based conversation key
        found_conversation_key = find_conversation_key(base_file_dir)

        # check for an embedded contextual key via a `.kalle_conversation` file
        if found_conversation_key:
          conversation_key = found_conversation_key.strip()
        else:
          # use the configured default if available
          conversation_key = os.environ.get("KALLE_DEFAULT_CONVERSATION", "default")

        self._conversation_key = conversation_key

    except Exception as e:
      console_stderr.print(
          Panel(
              f"[bold]CONFIG LOCATION:[/bold] {config_file_path}\n" f"{Rule(style='red')}\n" f"{str(e)}",
              title="[red bold]CONFIGURATION PROBLEM",
              style="red",
          )
      )
      if debug:
        console_stderr.print_exception(show_locals=True)
      sys.exit(110)

  # #####################################################
  # Prompt Templates
  def _load_prompts(self, prompts_config: PromptsConfig):
    from kalle.domain.PromptTemplate import PromptTemplate

    # Convert prompt templates
    prompt_templates = {}
    if prompts_config.kalle_system_prompt:
      prompt_templates["kalle_system_prompt"] = PromptTemplate(
          key="kalle_system_prompt",
          name="kalle_system_prompt",
          value=self._config.prompts.kalle_system_prompt
          or "Your name is Kalle. You are a helpful, confident, and friendly personal assistant.",
      )
    if prompts_config.base_tool_prompt:
      prompt_templates["base_tool_prompt"] = PromptTemplate(
          key="base_tool_prompt",
          name="base_tool_prompt",
          value=self._config.prompts.base_tool_prompt,
      )

      return prompt_templates

  # #####################################################
  # Patterns
  def _load_patterns(self, profiles):
    """Load patterns from the patterns directory."""
    import yaml
    from kalle.domain.Pattern import Pattern
    from kalle.domain.Constrainer import Constrainer, ConstrainerType
    from kalle.domain.PromptTemplate import PromptTemplate

    patterns = {}
    patterns_dir = self.patterns_dir
    if os.path.exists(patterns_dir):
      for filename in os.listdir(patterns_dir):
        try:
          if filename.endswith(".yaml"):
            pattern_key = filename[:-5]
            pattern_file_path = os.path.join(patterns_dir, filename)
            with open(pattern_file_path) as file:
              pattern_yaml = yaml.safe_load(file)

              system_prompt_template = None
              if "system_prompt_template" in pattern_yaml:
                system_prompt_template = PromptTemplate(
                    key="system_prompt_template", value=pattern_yaml["system_prompt_template"]
                )

              prompt_template = None
              if "prompt_template" in pattern_yaml:
                prompt_template = PromptTemplate(key="prompt_template", value=pattern_yaml["prompt_template"])

              constrainer = None
              if (
                  "constrainer" in pattern_yaml
                  and type(pattern_yaml["constrainer"]) is dict
                  and "type" in pattern_yaml["constrainer"]
              ):
                constrainer = Constrainer(
                    type=ConstrainerType(pattern_yaml["constrainer"]["type"]),
                    value=pattern_yaml["constrainer"]["value"],
                )

              profile = None
              if "profile" in pattern_yaml and pattern_yaml["profile"] in profiles.keys():
                profile = profiles[pattern_yaml["profile"]]

              patterns[pattern_key] = Pattern(
                  key=pattern_key,
                  name=pattern_yaml.get("name", None),
                  system_prompt_template=system_prompt_template,
                  prompt_template=prompt_template,
                  tools=pattern_yaml.get("tools", None),
                  constrainer=constrainer,
                  profile=profile,
              )
        except Exception as e:
          if self.debug:
            console_stderr.print(f"[orange1]Pattern {filename} is invalid, skipping: {e}")

    return patterns

  @property
  def config(self) -> KalleConfig:
    if self._config is None:
      raise Exception("KalleConfig not loaded")

    return self._config

  # #####################################################
  # Directories
  @property
  def config_dir(self) -> Optional[str]:
    kalle_config = user_config_dir(self._appname, self._appauthor)
    if os.environ.get("KALLE_CONFIG", None) is not None:
      kalle_config = os.path.dirname(os.environ.get("KALLE_CONFIG", None))  # type: ignore

    return kalle_config

  @property
  def data_dir(self) -> str:
    return (
        self._config.data_dir or os.environ.get("KALLE_DATA_DIR", None) or user_data_dir(self._appname, self._appauthor)
    )

  @property
  def cache_dir(self) -> str:
    return (
        self._config.cache_dir
        or os.environ.get("KALLE_CACHE_DIR", None)
        or user_cache_dir(self._appname, self._appauthor)
    )

  @property
  def patterns_dir(self) -> str:
    return (
        self._config.patterns_dir
        or os.environ.get("PATTERNS_DIR", None)
        or os.path.join(user_data_dir(self._appname, self._appauthor), "patterns")
    )

  # #####################################################
  # Debug
  @property
  def debug(self) -> bool:
    return self._debug

  # #####################################################
  # Conversation History
  @property
  def use_conversation_history(self) -> bool:
    return self._use_conversation_history

  # #####################################################
  # Memory
  @property
  def use_memory(self) -> bool:
    return self._use_memory

  # #####################################################
  # Format Output
  @property
  def format_output(self) -> bool:
    return (
        self._format_output
        if self._format_output is not None
        else os.environ.get("KALLE_FORMAT_OUTPUT", "false").lower() == "true"
    )

  # #####################################################
  # Conversation
  @property
  def conversation_key(self) -> Optional[str]:
    return self._conversation_key

  # #####################################################
  # API Keys
  def find_api_key(self, profile_name) -> Optional[str]:
    # Check if key is in the profile config
    profile = self._config.profiles.get(profile_name)
    if profile and profile.connector.key:
      return profile.connector.key

    # Check for key file
    if os.path.isfile(f"{self.config_dir}/{profile_name}.key"):
      with open(f"{self.config_dir}/{profile_name}.key") as file:
        return file.read().replace("\n", "")

    # Check environment variable
    env_key = f"KALLE_{profile_name.upper()}_API_KEY"
    return os.environ.get(env_key, None)

  # #####################################################
  # CONVERSATIONS
  @property
  def conversation_dir(self) -> str:
    return os.path.normpath(f"{self.data_dir}/conversations/")

  # #####################################################
  # Models Map
  @property
  def models_map(self) -> Dict[str, Any]:
    return self._config.models_map
