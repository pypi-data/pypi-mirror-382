# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2

# #############################################################################
# Imports
# #############################################################################
import time

import json
import os
import sys
import re

from typing import Optional
from platformdirs import user_config_dir, user_data_dir, user_cache_dir

from rich.box import HORIZONTALS, ROUNDED
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.tree import Tree
from rich.markdown import Markdown
from rich.syntax import Syntax

# Utilities
from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.util.ConversationTools import ConversationTools
from kalle.lib.util.ProfileManager import ProfileManager
from kalle.lib.util.PromptManager import PromptManager

# Domain
from kalle.domain.Conversation import ConversationMessage
from kalle.domain.Context import Context
from kalle.domain.Constrainer import Constrainer
# from kalle.domain.LLMRequest import LLMRequest


class Kalle:

  def __init__(self, /, base_file_dir: Optional[str] = None, debug: bool = False):
    self.appname = "kalle"
    self.appauthor = "fe2"

    self.conversing = False
    self.console = Console()
    self.console_stderr = Console(file=sys.stderr)

    self.panel_format = ROUNDED

    if base_file_dir is None:
      self.base_file_dir = os.getcwd()
    else:
      self.base_file_dir = base_file_dir

    # cache in kalle's cache
    os.environ["TIKTOKEN_CACHE_DIR"] = os.path.join(user_cache_dir(self.appname, self.appauthor), "tiktoken_cache")

    # Suppress non-actionable warnings when using kalle unless we're debugging
    if not debug:
      os.environ["TRANSFORMERS_VERBOSITY"] = "error"
      os.environ["TOKENIZERS_PARALLELISM"] = "false"
      os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
      from transformers.utils import logging

      logging.disable_progress_bar()
      import warnings

      warnings.filterwarnings("ignore")

    # #############################################################################################################
    # load the config
    self.check_dirs()
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        base_file_dir=base_file_dir or os.getcwd(),
        debug=debug,
    )
    self.conversation_tools = ConversationTools(self.config_manager)
    if self.config_manager.config.interactive_style == "lines":
      self.panel_format = HORIZONTALS

  def check_dirs(self):
    # Ensure relevant directories exist
    config_dir = user_config_dir(self.appname, self.appauthor)
    cache_dir = user_cache_dir(self.appname, self.appauthor)
    data_dir = user_data_dir(self.appname, self.appauthor)

    self.check_and_create_dir(config_dir)  # config dir
    self.check_and_create_dir(data_dir)  # data dir
    self.check_and_create_dir(os.path.join(data_dir, "conversations"))  # conversations dir
    self.check_and_create_dir(cache_dir)  # cache dir
    self.check_and_create_dir(os.path.join(cache_dir, "tiktoken_cache"))  # tiktoken cache dir
    self.check_and_create_dir(os.path.join(cache_dir, "tokens"))  # tokens cache dir

  def check_and_create_dir(self, dir_path):
    if not os.path.exists(dir_path):
      try:
        self.console_stderr.print(f"[yellow]Creating directory {dir_path}")
        os.makedirs(dir_path)
      except Exception:
        self.console_stderr.print(f"[red]Could not create {dir_path} directory")

  async def show_embedding(self, text: Optional[str]):
    if text is None:
      self.console_stderr.print("[red]NEED TEXT TO EMBED")
      return

    response = await self.memory_manager.embed(text)
    if isinstance(response, list):
      print(json.dumps(response, indent=4))

  def show_history(self, conversation_key: Optional[str] = None, format_output: Optional[bool] = False):
    if conversation_key is None:
      self.console_stderr.print("[red]NO CONVERSATION TO SHOW HISTORY FOR")
      return

    self.console.print(f"[bold magenta]CONVERSATION HISTORY FOR: [italic]{conversation_key}")
    conversation = self.conversation_tools.load_conversation(conversation_key=conversation_key)
    ac = ""
    al = "center"
    for c in conversation.get_messages():
      ac = "blue"
      al = "right"
      name = "User"
      if c["role"] == "assistant":
        ac = "orange1"
        al = "left"
        name = "kalle"

      if format_output:
        self.console.print(
            Panel(
                Syntax(
                    f"{c['content']}",
                    lexer="text",
                    word_wrap=True,
                ),
                box=self.panel_format,
                padding=-1,
                subtitle=f"[{ac} bold]< {name} >",
                subtitle_align=al,
                border_style=ac,
            )
        )
      else:
        self.console.print(Rule(style=ac))
        self.console.print(f"[bold {ac}]{name}: ")
        self.console.print(Rule(style=ac))
        self.console.print(f"{c['content']}")

  def get_time_since_last(self, timestamp: float):
    """Gets the time since the last message to kalle."""
    from datetime import datetime

    now = datetime.now()
    time = datetime.fromtimestamp(timestamp)
    delta = now - time
    return delta

  def humanize_delta(self, delta):
    """Convert a timedelta object to a human-readable string."""
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
      return f"Time since last message was {days} days ago."
    elif hours > 0:
      return f"Time since last message was {hours} hours ago."
    elif minutes > 0:
      return f"Time since last message was {minutes} minutes ago."
    else:
      return f"Time since last message was {seconds} seconds ago."

  def list_conversations(self):
    conversations = self.conversation_tools.list_conversations()
    self.console_stderr.print("[bold magenta]CONVERSATIONS:")
    for c in conversations:
      self.console.print(f"{c}", highlight=False)

  def handle_inline_commands(self, text: Optional[str] = None):
    if text is None:
      return

    if text.startswith("reset conversation"):
      if (
          self.context.use_conversation_history
          and self.context.conversation_key is not None
          and self.conversation.conversation != []
      ):
        self.conversation_tools.archive_conversation(self.context.conversation_key)

        self.console.print("[green]Conversation reset")
        sys.stdout.flush()
        if not self.interactive:
          sys.exit(0)
        else:
          return "reset_conversation"
      else:
        self.console.print("[dark_orange]No conversation to reset")
        sys.stdout.flush()
        if not self.interactive:
          sys.exit(0)
        else:
          return "no_conversation"

    if text.startswith("set conversation"):
      conversation_name = text.split("set conversation ")[1].strip()
      conversation_file_path = os.path.join(self.base_file_dir, ".kalle_conversation")

      if os.path.exists(conversation_file_path):
        self.console_stderr.print(
            f"[red]Warning: A conversation file already exists at {conversation_file_path}, not overwriting."
        )
        if not self.interactive:
          sys.exit(27)
        else:
          return "conversation_exists"
      else:
        with open(conversation_file_path, "w") as f:
          f.write(conversation_name)
        self.console.print(
            f"[green]Conversation file created at {conversation_file_path} for conversation {conversation_name}"
        )
      if not self.interactive:
        sys.exit(0)
      else:
        return "set_conversation"

    if text.startswith("unset conversation"):
      conversation_file_path = os.path.join(self.base_file_dir, ".kalle_conversation")

      try:
        os.remove(conversation_file_path)
        self.console.print(f"[green]Conversation file removed at {conversation_file_path}")
      except FileNotFoundError:
        self.console_stderr.print(f"[red]File not found to remove at {conversation_file_path}")
        if not self.interactive:
          sys.exit(28)
        else:
          return "file_not_found"
      except Exception as e:
        self.console_stderr.print(f"[red]An error occurred removing conversation file {conversation_file_path}: {e}")
        if not self.interactive:
          sys.exit(29)
        else:
          return "remove_error"

      if not self.interactive:
        sys.exit(0)
      else:
        return "unset_conversation"

  def load_pattern(self, pattern_key: str):
    if pattern_key is not None:
      if pattern_key in self.config_manager.patterns:
        return self.config_manager.patterns[pattern_key]
      else:
        self.console_stderr.print(f"[red]Pattern '{pattern_key}' is not found.")
        if not self.interactive:
          exit(17)
        else:
          return None

  def show_debug_info(self):
    if self.config_manager.debug:
      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]USE MEMORY:[/bold] {self.context.use_conversation_history}",
                  f"[magenta][bold]FORMAT OUTPUT:[/bold] {self.config_manager.format_output}",
                  f"[magenta][bold]CONVERSATIONS:[/bold] {len(self.conversation_tools.list_conversations())}",
              ),
              box=self.panel_format,
              title="[bold magenta]GENERAL DEBUG INFO",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]CONVERSATION KEY:[/bold] {self.config_manager.conversation_key}",
                  f"[magenta][bold]CONVERSATION ENTRIES:[/bold] {len(self.conversation.conversation) - 1}",
                  f"[magenta][bold]LONG CONVERSATION HANDLING:[/bold] {self.context.long_conversation_handling}",
              ),
              box=self.panel_format,
              title="[bold magenta]CONVERSATION",
              style="magenta",
          )
      )

      model_tree = Tree(f"[magenta][bold]MODEL:[/bold] {type(self.profile_manager.model)}")
      model_tree.add(f"[magenta][bold]MODEL_STRING:[/bold] {self.profile_manager.model.name}")
      model_tree.add(f"[magenta][bold]CONTEXT_SIZE:[/bold] {self.profile_manager.model.context_size}")
      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]PROFILE:[/bold] {self.profile_manager.profile.key}",
                  f"[magenta][bold]CONNECTOR:[/bold] {type(self.profile_manager.connector)}",
                  model_tree,
              ),
              box=self.panel_format,
              title="[bold magenta]PROFILE",
              style="magenta",
          )
      )

      pattern_tree = Tree(f"[magenta][bold]PATTERN:[/bold] {self.context.args_pattern_key}")
      pattern_tree.add(f"[magenta][bold]NAME:[/bold] {self.pattern.name if self.pattern is not None else None}")
      self.console_stderr.print(
          Panel(
              Group(
                  pattern_tree,
              ),
              box=self.panel_format,
              title="[bold magenta]PATTERN",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]SYSTEM_PROMPT:[/bold]\n{self.context.args_system_prompt}",
              ),
              box=self.panel_format,
              title="[magenta]ARGS SYSTEM PROMPT",
              style="magenta",
          )
      )

      config_system_prompt = self.config_manager.prompts.get("kalle_system_prompt", None)
      config_system_prompt = config_system_prompt.value if config_system_prompt is not None else None
      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]SYSTEM_PROMPT:[/bold]\n{config_system_prompt}",
              ),
              box=self.panel_format,
              title="[magenta]CONFIG SYSTEM PROMPT",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"""[magenta][bold]PATTERN Constrainer:[/bold]
  [bold]TYPE:[/bold] {self.pattern.constrainer.type if self.pattern is not None and self.pattern.constrainer is not None else None}
  [bold]VALUE:[/bold] {self.pattern.constrainer.value if self.pattern is not None and self.pattern.constrainer is not None else None}
""",
              ),
              box=self.panel_format,
              title="[magenta]CONSTRAINER",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]SYSTEM_PROMPT:[/bold]\n{self.pattern.system_prompt_template if self.pattern is not None else None}",
              ),
              box=self.panel_format,
              title="[magenta]PATTERN SYSTEM PROMPT TEMPLATE",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]SYSTEM_PROMPT:[/bold]\n{self.conversation.metadata.system_prompt if self.conversation.metadata is not None else None}",
              ),
              box=self.panel_format,
              title="[magenta]CONVERSATION SYSTEM PROMPT",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]SYSTEM_PROMPT_TOKEN_COUNT (approximate):[/bold] {self.system_prompt_tokens}",
                  f"[magenta][bold]SYSTEM_PROMPT:[/bold]\n{self.system_prompt}",
              ),
              box=self.panel_format,
              title="[bold magenta]FINAL SYSTEM PROMPT",
              style="magenta",
          )
      )

      self.console_stderr.print(
          Panel(
              f"[magenta]{self.rag_content}",
              box=self.panel_format,
              title="[bold magenta]MEMORY CONTENTS",
              style="magenta",
          )
      )

      tools = []
      if self.tool_handler is not None:
        for t, _ in self.tool_handler.get_tools().items():
          tools.append(f"[magenta]- {t}")

        self.console_stderr.print(
            Panel(
                Group(
                    *tools,
                ),
                box=self.panel_format,
                title="[bold magenta]TOOLS",
                style="magenta",
            )
        )

      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta][bold]PROMPT_TOKEN_COUNT (approximate):[/bold] {self.prompt_tokens}",
                  "[magenta][bold]PROMPT:[/bold]",
                  self.compiled_prompt[-1]["content"],
                  # Syntax(json.dumps(self.compiled_prompt[0]["content"], indent=4), "json", word_wrap=True),
              ),
              box=self.panel_format,
              title="[bold magenta]USER PROMPT",
              style="magenta",
          )
      )

  def llm_toolchoice_status_line(self, profile_manager) -> str:
    conv_disp = ""
    if self.context.conversation_key is not None:
      conv_disp = f" (CONVERSATION: [italic]{self.context.conversation_key}[/italic])"

    status_line = f"[bold yellow]Making tool choice ({profile_manager.profile.connector.name}/{profile_manager.model.key}){conv_disp}..."

    return status_line

  def llm_toolcall_status_line(self) -> str:
    conv_disp = ""
    if self.context.conversation_key is not None:
      conv_disp = f" (CONVERSATION: [italic]{self.context.conversation_key}[/italic])"

    status_line = f"[bold yellow]Making tool call request ({self.profile_manager.profile.connector.name}/{self.profile_manager.model.key}){conv_disp}..."

    return status_line

  def llm_request_status_line(self) -> str:
    conv_disp = ""
    if self.context.conversation_key is not None:
      conv_disp = f" (CONVERSATION: [italic]{self.context.conversation_key}[/italic])"

    status_line = f"[bold yellow]Making LLM request ({self.profile_manager.profile.connector.name}/{self.profile_manager.model.key}){conv_disp}..."

    return status_line

  def extract_internal_contents(self, text):
    # Extract think contents
    match_pattern = r"<think>(.*?)</think>"
    matches = re.findall(match_pattern, text, re.DOTALL)
    think_response = [{"key": "think", "value": v.strip()} for v in matches]
    remove_pattern = re.compile(r"<think>.*</think>", re.DOTALL)
    text = re.sub(remove_pattern, "", text)

    # Extract kalle_core contents
    match_pattern = r".kalle_core[>_)](.*?)./kalle_core."
    matches = re.findall(match_pattern, text, re.DOTALL)
    kalle_core_response = [{"key": "kalle_core", "value": v.strip()} for v in matches]
    remove_pattern = re.compile(r".kalle_core.*/kalle_core.", re.DOTALL)
    text = re.sub(remove_pattern, "", text)

    # Extract tool_response contents
    match_pattern = r".tool_response[>_)](.*?)./kalle_core."
    matches = re.findall(match_pattern, text, re.DOTALL)
    tool_response = [{"key": "tool_response", "value": v.strip()} for v in matches]
    remove_pattern = re.compile(r".tool_response.*/tool_response.", re.DOTALL)
    text = re.sub(remove_pattern, "", text)

    # Combine responses
    response = text.strip(), think_response + kalle_core_response + tool_response

    return response

  async def process_long_conversation(
      self, historic_conversation: list, handling_mode: str
  ) -> tuple[list, Optional[str]]:
    """Process conversation history based on the specified handling mode.

    Args:
        historic_conversation: List of conversation messages
        handling_mode: String specifying the handling mode (none, tail:N, summary:N)

    Returns:
        Processed conversation history
    """
    if handling_mode is None or handling_mode == "none":
      return historic_conversation, None

    if handling_mode.startswith("tail:"):
      try:
        # Extract the number of message pairs to keep
        n = int(handling_mode.split(":")[1])
        # Each pair consists of a user message and an assistant message
        # So we need to keep the last n*2 messages
        messages_to_keep = n * 2
        if len(historic_conversation) <= messages_to_keep:
          return historic_conversation, None
        return historic_conversation[-messages_to_keep:], None
      except (ValueError, IndexError):
        self.console_stderr.print(f"[red]Invalid tail format: {handling_mode}. Using full conversation.")
        return historic_conversation, None

    elif handling_mode.startswith("summary:"):
      try:
        # Extract the number of recent messages to keep
        n = int(handling_mode.split(":")[1])

        if len(historic_conversation) <= n:
          return historic_conversation, None

        # Split conversation into parts to summarize and parts to keep
        messages_to_summarize = historic_conversation[:-n]
        messages_to_keep = historic_conversation[-n:]

        # Create a summary request
        summary_prompt = "Please provide a concise summary of the following conversation history, capturing key points, decisions, and context. Begin with 'CONVERSATION SUMMARY:':\n\n"
        for msg in messages_to_summarize:
          role = msg["role"].capitalize()
          content = msg["content"]
          summary_prompt += f"{role}: {content}\n\n"

        # Make a request to summarize the older conversation
        with self.console_stderr.status("[bold yellow]Summarizing older conversation history..."):
          summary_response = await self.profile_manager.connector.request(
              system_prompt="You are a helpful assistant that creates concise summaries of conversations. Focus on key information, decisions, and context that would be important for continuing the conversation.",
              messages=[{"role": "user", "content": summary_prompt}],
              model_params=self.profile_manager.profile.model_params,
          )

        remove_pattern = re.compile(r"<think>.*</think>", re.DOTALL)
        summary_response = re.sub(remove_pattern, "", summary_response)

        # Return the summary plus the recent messages
        return messages_to_keep, summary_response

      except (ValueError, IndexError):
        self.console_stderr.print(f"[red]Invalid summary format: {handling_mode}. Using full conversation.")
        return historic_conversation, None
      except Exception as e:
        self.console_stderr.print(f"[red]Error creating summary: {e}. Using full conversation.")
        return historic_conversation, None

    else:
      self.console_stderr.print(
          f"[red]Unknown long conversation handling mode: {handling_mode}. Using full conversation."
      )
      return historic_conversation

  async def run(
      self,
      /,
      param_content: str,
      piped_content: Optional[str] = None,
      embed: bool = False,
      knowledgebase: Optional[str] = None,
      store: bool = False,
      doc_reference: Optional[str] = None,
      query: Optional[str] = None,
      use_conversation_history: bool = False,
      long_conversation_handling: Optional[str] = None,
      constrainer: Optional[Constrainer] = None,
      interactive: bool = False,
      format_output: bool = True,
      conversation_key: Optional[str] = None,
      args_system_prompt: Optional[str] = None,
      args_profile_key: Optional[str] = None,
      args_pattern_key: Optional[str] = None,
      args_model_params: Optional[list] = None,
      follow_uris: Optional[str] = None,
      use_memory: bool = False,
      tool_list: Optional[list] = None,
      use_tools: bool = False,
      use_voice: bool = False,
      args_model_string: Optional[str] = None,
      debug: bool = False,
  ):

    self.interactive = interactive
    self.format_output = format_output
    self.embed = embed
    self.store = store
    self.query = query
    self.use_memory = use_memory
    self.context = Context(
        base_file_dir=self.base_file_dir,
        use_conversation_history=use_conversation_history,
        long_conversation_handling=long_conversation_handling,
        param_content=param_content,
        piped_content=piped_content,
        conversation_key=conversation_key,
        args_system_prompt=args_system_prompt,
        args_profile_key=args_profile_key,
        args_pattern_key=args_pattern_key,
        args_model_string=args_model_string,
        args_model_params=args_model_params,
        constrainer=constrainer,
        follow_uris=follow_uris,
        use_memory=use_memory,
        doc_reference=doc_reference,
        knowledgebase=knowledgebase,
        tool_list=tool_list,
        use_tools=use_tools or False,
        use_voice=use_voice or False,
        debug=debug,
    )

    content = self.context.param_content

    # #############################################################################################################
    # load the config
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=self.context.conversation_key,
        base_file_dir=self.base_file_dir,
        use_conversation_history=self.context.use_conversation_history,
        use_memory=self.context.use_memory,
        format_output=self.format_output,
        debug=self.context.debug,
    )
    self.conversation_tools = ConversationTools(self.config_manager)

    # #############################################################################################################
    # load a pattern (if specified)
    self.pattern = self.load_pattern(self.context.args_pattern_key) if self.context.args_pattern_key else None

    # #############################################################################################################
    # set up things that depend on the config

    # set the active profile key
    self.profile_key = None
    if self.context.args_profile_key is not None:
      if self.context.args_profile_key in self.config_manager.config.profiles.keys():
        self.profile_key = self.context.args_profile_key
      else:
        self.console_stderr.print(f"[red]Profile {self.context.args_profile_key} is not found")
        if not self.interactive:
          sys.exit(8)
        else:
          return

    # set the URI handler if needed
    self.uri_handler = None
    if self.context.follow_uris is not None:
      from kalle.lib.util.URIHandler import URIHandler

      self.uri_handler = URIHandler(self.config_manager, self.base_file_dir, console_stderr=self.console_stderr)

    # set the tool handler if needed
    self.tool_handler = None
    if self.context.use_tools:
      from kalle.lib.util.ToolHandler import ToolHandler

      self.tool_handler = ToolHandler(
          self.config_manager,
          base_file_dir=self.base_file_dir,
          tool_list=self.context.tool_list,
          console_stderr=self.console_stderr,
      )

    # #############################################################################################################
    # load the stored conversation
    if self.context.conversation_key is not None:
      self.conversation = self.conversation_tools.load_conversation(conversation_key=self.context.conversation_key)

    # set up an empty one if a conversation key isn't specified
    if not hasattr(self, "conversation"):
      self.conversation = self.conversation_tools.empty_conversation

    # handle on of a number of "commands" that can be presented via the prompt
    command_result = self.handle_inline_commands(self.context.param_content)
    if command_result is not None and self.interactive:
      # In interactive mode, return to let the CLI handle the command result
      return

    # #############################################################################################################
    # load the profile (connection and model)
    # look for the profile key in:
    # - a passed conversation key
    # - the conversation metadata
    conversation_profile_key = None
    if self.conversation.metadata.profile is not None:
      conversation_profile_key = self.conversation.metadata.profile.key

    if self.pattern is not None and self.pattern.profile is not None:
      self.profile_key = self.pattern.profile.key
    self.profile_key = self.profile_key or conversation_profile_key or "base"

    self.profile_manager = ProfileManager(
        self.config_manager,
        self.profile_key,
        model_string=self.context.args_model_string,
        console_stderr=self.console_stderr,
    )

    # prepare the system, user prompts
    historic_conversation = self.conversation.get_messages()
    self.interaction_context = []

    # Process long conversation based on handling mode
    if self.context.long_conversation_handling:
      historic_conversation, summary = await self.process_long_conversation(
          historic_conversation, self.context.long_conversation_handling
      )
      self.interaction_context.append(summary)

    from datetime import datetime

    datetime = datetime.now().astimezone()
    time_since_last_message = "This is the first message in this conversation."
    if len(historic_conversation) > 0:
      last_message_index = len(historic_conversation) - 2
      if last_message_index < 0:
        last_message_index = 0
      last_message_timestamp = self.conversation.conversation[last_message_index].timestamp
      if last_message_timestamp is not None:
        time_since_last_message = self.humanize_delta(self.get_time_since_last(last_message_timestamp))

    self.interaction_context.append(f"CURRENT DATE AND TIME: {datetime}")
    self.interaction_context.append(f"TIME SINCE LAST MESSAGE: {time_since_last_message}")

    # if we're in a conversation, there may be <kalle_core*></kalle_core*> tags as part of the LLM
    # responses. We want to filter them out of the response and ensure they're added to the end of
    # the system prompt
    if len(historic_conversation) > 0:
      kc = None
      idx = len(self.conversation.conversation) - 1
      while kc is None and idx >= 0:
        if (
            self.conversation.conversation[idx].internals is not None
            and len(self.conversation.conversation[idx].internals) > 0
        ):
          for i in self.conversation.conversation[idx].internals:
            if i["key"] == "kalle_core" and i["value"] is not None:
              kc = f"---\n<kalle_core>{str(i['value'])}</kalle_core>"
          break
        idx += -1

      # consider making interaction context item an object
      # from there include a weight/importance option so we can control the ordering
      self.interaction_context.append(kc)

    # parse and unroll URIs
    working_param_content = self.context.param_content
    working_piped_content = self.context.piped_content
    with self.console_stderr.status("[bold yellow]Parsing and enriching request..."):
      if self.uri_handler is not None:
        if self.context.follow_uris is not None:
          working_param_content, _ = self.uri_handler.parse_content(working_param_content)
        if self.context.follow_uris == "all":
          working_piped_content, _ = self.uri_handler.parse_content(working_piped_content)

    prompt_manager = PromptManager(
        self.config_manager,
        system_prompt_template=self.pattern.system_prompt_template if self.pattern else None,
        system_prompt=self.context.args_system_prompt,
        prompt_template=self.pattern.prompt_template if self.pattern else None,
        piped_content=working_piped_content,
        param_content=working_param_content,
        interaction_context=self.interaction_context,
    )

    self.system_prompt = prompt_manager.compile_system_prompt()

    compiled_content = prompt_manager.compile_prompt()

    # @TODO
    # adding:
    # * current date and time
    # * time since last message
    # * kalle_core
    # * user's name
    # * personal notes about the user
    # * relationship summary about user

    # add the compiled content to the message for the llm
    current_conversation_message = ConversationMessage(
        timestamp=time.time(),
        profile=self.profile_manager.profile,
        system_prompt=self.context.args_system_prompt,
        role="user",
        piped_content=self.context.piped_content,
        param_content=self.context.param_content,
        content=compiled_content,
    )
    current_prompt = current_conversation_message.get_message()

    # add the current message to the conversation
    self.conversation.conversation.append(current_conversation_message)

    # prompt to send to the LLM
    self.compiled_prompt = []

    # add the conversation if we're permitting conversation memory
    if self.config_manager.use_conversation_history or self.interactive:
      self.compiled_prompt += historic_conversation

    self.compiled_prompt += (current_prompt,)

    if self.profile_manager.model is None:
      self.console_stderr.print(f"[red]Error: Model not available in models_map {self.profile_manager.profile.model}")
      if not self.interactive:
        sys.exit(18)
      else:
        return

    if self.embed or self.store or self.query or self.use_memory:
      from kalle.lib.util.MemoryManager import MemoryManager

      embedding_profile = ProfileManager(self.config_manager, "embed", console_stderr=self.console_stderr)
      reranking_profile = ProfileManager(self.config_manager, "rerank", console_stderr=self.console_stderr)
      relevance_profile = ProfileManager(self.config_manager, "relevance", console_stderr=self.console_stderr)
      enrichment_profile = ProfileManager(self.config_manager, "base", console_stderr=self.console_stderr)
      self.memory_manager = MemoryManager(
          {
              "data_dir": self.config_manager.data_dir,
              "memory": self.config_manager.config.memory,
          },
          embedding_connector=embedding_profile.connector,
          enrichment_connector=enrichment_profile.connector,
          reranking_connector=reranking_profile.connector,
          relevance_connector=relevance_profile.connector,
          db_name=self.context.knowledgebase,
      )

    if self.embed:
      embed_content = param_content
      if piped_content is not None:
        embed_content += piped_content
      await self.show_embedding(embed_content)
      if not self.interactive:
        sys.exit(0)
      else:
        return

    if self.store:
      store_content = param_content
      if piped_content is not None:
        store_content += piped_content
      await self.memory_manager.store(store_content, ref=self.context.doc_reference, enrich=True)
      self.console_stderr.print("[green]Content stored to memory")
      if not self.interactive:
        sys.exit(0)
      else:
        return

    if self.query:
      query_content = param_content
      if piped_content is not None:
        query_content += piped_content
      results = await self.memory_manager.query(query_content)

      for i in results:
        print("-" * 80)
        print(f"DOCUMENT REFERENCE: {i['ref']}")
        print(f"RELEVANCE SCORE: {i['relevance_score']}")
        print(f"DISTANCE: {i['distance']}")
        print(f"CONTENT:\n{i['text']}")
      if not self.interactive:
        sys.exit(0)
      else:
        return

    self.rag_content = None
    if self.context.use_memory:
      with self.console_stderr.status("[bold yellow]Enhancing request with memories..."):
        # @TODO push into promptmanager?

        query_content = param_content
        if piped_content is not None:
          query_content += piped_content
        results = await self.memory_manager.query(query_content)

        self.rag_content = "The following knowledgebase content is possibly related memories that can be used in responding to the query:\n\n<KNOWLEDGEBASE_CONTENT>\n"
        for i in results:
          self.rag_content += "---\n"
          if i["ref"] is not None:
            self.rag_content += f"DOC REFERENCE: {i['ref']}\n"
          self.rag_content += f"RELEVANCE SCORE: {i['relevance_score']}\n"
          self.rag_content += f"CONTENT:\n{i['text']}\n\n"

        self.rag_content += "</KNOWLEDGEBASE_CONTENT>"
        self.rag_content += "The previous information between the '<KNOWLEDGEBASE_CONTENT></KNOWLEDGEBASE_CONTENT>' tags is available to provide a response, but using any of the contents there is optional. DO NOT talk about the information before this point, use it if it seems relevant.\n---\n"
        self.compiled_prompt[-1]["content"] = f"{self.rag_content}\n\n{self.compiled_prompt[-1]['content']}"

    try:
      self.system_prompt_tokens = self.profile_manager.tokenizer.get_conversation_tokens(
          [{"role": "system", "content": self.system_prompt}]
      )
      self.prompt_tokens = self.profile_manager.tokenizer.get_conversation_tokens(self.compiled_prompt)
    except Exception as e:
      self.console_stderr.print(f"[red][bold]ERROR:[/bold] could not get prompt tokens: {e}")
      if self.config_manager.debug:
        self.console_stderr.print_exception(show_locals=False)

      if not self.interactive:
        sys.exit(8)
      else:
        return

    # Possible future pattern to refactor into
    # self.llm_request = LLMRequest(
    #        key = "",
    #        system_prompt = "",
    #        piped_prompt = "",
    #        args_prompt = "",
    #        tools = "",
    #        constrainer = "",
    #        connector = "",
    #        model = "",
    #    )

    # constrainer if one is available
    constrainer = self.context.constrainer or (self.pattern.constrainer if self.pattern is not None else None)

    self.show_debug_info()

    response = ""
    tool_prompt = None
    tool_response = None
    tooled_request = None
    tool_call_results = []
    if self.system_prompt_tokens + self.prompt_tokens > self.profile_manager.model.context_size - 100:
      self.console_stderr.print(
          f"[red]Warning: length of prompt exceeds the current max context length ({self.profile_manager.model.context_size}), aborting."
      )
      if not self.interactive:
        sys.exit(9)
      else:
        return
    else:
      # fetch a response
      if (
          self.context.use_tools
          and len(self.context.tool_list) == 0
          and self.config_manager.config.smart_tool_selection
      ):

        tool_choice_profile = ProfileManager(self.config_manager, "toolchooser", console_stderr=self.console_stderr)
        tool_choices = ""
        smart_tool_list = []
        with self.console_stderr.status(self.llm_toolchoice_status_line(tool_choice_profile)):
          for tk, tool in self.tool_handler.get_tools().items():
            tool_choices += f"---\n# TOOL: {tk}\n{tool.get_prompt()}\n\n"

          tool_prompt_message = self.compiled_prompt[-1]["content"]
          tool_selection_resp = await tool_choice_profile.connector.request(
              """You are a tool chooser.
You review a request along with a set of possible tools and respond with the list of tools that could be relevant.

Only respond with the tool list in JSON format like this:

<tool_choices>[\"update_file\", \"desktop_notification\"]</tool_choices>

If no tools are applicable reply with an empty list like this:

<tool_choices>[]</tool_choices>""",
              [
                  {
                      "role": "user",
                      "content": f"""Here is the list of tools:

{tool_choices}

Provide the relevant tools to this request:

{tool_prompt_message}

/nothink""",
                  }
              ],
              model_params={"temperature": 0.1},
          )

          match_pattern = r".tool_choices[>_)](.*?)./tool_choices."
          matches = re.findall(match_pattern, tool_selection_resp, re.DOTALL)

          if len(matches) > 0:
            try:
              smart_tool_list = json.loads(matches[0])
            except json.JSONDecodeError:
              self.console_stderr.print(f"[red][bold]ERROR:[/bold] Could not decode tool selection JSON {matches[0]}")
              if not self.interactive:
                sys.exit(10)
              else:
                return

        if len(smart_tool_list) > 0:
          self.context.tool_list = smart_tool_list
          self.tool_handler.set_tools(smart_tool_list)

      do_tool_call = self.context.use_tools and (
          (self.context.tool_list is not None and len(self.context.tool_list) > 0)
          or not self.config_manager.config.smart_tool_selection
      )

      if do_tool_call:
        # compile the system prompt specific to the available tools
        compiled_tool_prompt = prompt_manager.compile_tool_prompt(
            self.tool_handler.get_tools() if self.tool_handler is not None else None
        )
        tool_prompt = compiled_tool_prompt

        if self.config_manager.debug:
          self.console_stderr.print(
              Panel(
                  f"[magenta]{compiled_tool_prompt}",
                  box=self.panel_format,
                  title="[bold magenta]COMPILED TOOL PROMPT",
                  style="magenta",
              )
          )

        tool_prompt_message = {
            "role": "user",
            "content": f"{self.compiled_prompt[-1]['content']}\n{compiled_tool_prompt}\n\\nothink",
        }

        toolcall_status_line = self.llm_toolcall_status_line()
        with self.console_stderr.status(toolcall_status_line):

          tool_response = await self.profile_manager.connector.request(
              self.system_prompt,
              self.compiled_prompt[0:-2] + [tool_prompt_message],
              model_params={"temperature": 0.1},
          )

        if self.config_manager.debug:
          self.console_stderr.print(
              Panel(
                  f"[magenta]{tool_response}",
                  box=self.panel_format,
                  title="[bold magenta]TOOLING RESPONSE",
                  style="magenta",
              )
          )

        # invoke the tools returned by the preliminary response and compile into another llm request
        if tool_response is not None:

          functions, bodies = self.tool_handler.preprocess(tool_response)

          if len(functions) > 0:
            with self.console_stderr.status("[bold yellow]Processing tool calls..."):
              tooled_request = (
                  await self.tool_handler.process(functions, bodies) if self.tool_handler is not None else ""
              )
              tool_call_results.append(tooled_request)

              tooled_request += f"""

---
<tool_response_instructions>
The prior content before this message is the results of a set of tool call responses:

This was the original user request:
<original_request>
{self.compiled_prompt[-1]['content']}
</original_request>

Your response MUST be based on the tool call response.
The user's request is provided ONLY for context.
</tool_response_instructions>
"""

              if tooled_request is None or tooled_request == "":
                tooled_request = "Report to the user that you ran into an internal issue completing the user's request and ask the user to try again. Don't make any promises."

              # make the final request to the llm
            with self.console_stderr.status(self.llm_request_status_line()):
              response = await self.profile_manager.connector.request(
                  system_prompt=self.system_prompt,
                  messages=[{"role": "user", "content": tooled_request}],
                  model_params=self.profile_manager.profile.model_params,
                  constrainer=constrainer,
              )
          else:
            do_tool_call = False

      if not do_tool_call:
        # make the request to the llm
        with self.console_stderr.status(self.llm_request_status_line()):
          try:
            response = await self.profile_manager.connector.request(
                system_prompt=self.system_prompt,
                messages=self.compiled_prompt,
                model_params=self.profile_manager.profile.model_params,
                constrainer=constrainer,
            )
          except Exception:
            if self.config_manager.debug:
              self.console_stderr.print_exception(show_locals=False)

    if not response:
      self.console_stderr.print("[red]AN ERROR OCCURRED WHILE AWAITING A RESPONSE")
      if not self.interactive:
        sys.exit(10)
      else:
        return

    visible_response, internals = self.extract_internal_contents(response)

    # conversation.metadata.system_prompt = self.system_prompt
    self.conversation.metadata.profile = self.profile_manager.profile
    self.conversation.conversation.append(
        ConversationMessage(
            timestamp=time.time(),
            profile=self.profile_manager.profile,
            role="assistant",
            tool_prompt=tool_prompt,
            tool_response=tool_response,
            tool_call_results=tool_call_results,
            tooled_request=tooled_request,
            content=visible_response,
            internals=internals,
        )
    )
    if self.config_manager.use_conversation_history:
      self.conversation_tools.persist_conversation(self.conversation, conversation_key=self.context.conversation_key)

    if self.context.debug:
      for i in internals:
        title = "INTERNALS"
        if (i["key"]) != "":
          title += f" - {i['key']}"

        self.console_stderr.print(
            Panel(
                i["value"],
                box=self.panel_format,
                title=title,
                border_style="magenta",
            )
        )

    if self.config_manager.format_output:
      if self.interactive and self.config_manager.config.interactive_style == "lines":
        self.console.print(
            Rule(style="orange1"),
            Markdown(f"{visible_response}"),
            Rule(title="[orange1 bold]─ < Kalle >", align="left", style="orange1"),
        )
      elif self.interactive and self.config_manager.config.interactive_style == "bubble":
        self.console.print(
            Panel(
                Markdown(f"{visible_response}"),
                box=self.panel_format,
                subtitle="[bold]< Kalle >",
                subtitle_align="left",
                border_style="orange1",
            )
        )
      else:
        self.console.print(Markdown(f"{visible_response}"))
    else:
      self.console.print(f"{visible_response}", highlight=None)
    if self.context.use_voice and self.config_manager.config.voicebox is not None:
      from kalle.lib.util.Speak import Speak

      speak = Speak(
          {
              "voicebox_uri": self.config_manager.config.voicebox.uri,
              "api_key": self.config_manager.config.voicebox.api_key,
              "voice": self.config_manager.config.voicebox.voice,
              "speed": self.config_manager.config.voicebox.speed,
              "debug": self.context.debug,
          },
          console_stderr=self.console_stderr,
      )
      await speak.say(visible_response)

    sys.stdout.flush()
