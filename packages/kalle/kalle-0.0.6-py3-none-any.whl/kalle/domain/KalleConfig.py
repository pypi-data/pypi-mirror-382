from typing import Optional, Dict, Any
from enum import Enum
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from pydantic import BaseModel, Field, model_validator
import os
import yaml

from kalle.domain.ModelConfig import ModelConfig
from kalle.domain.Profile import Profile


class InteractiveStyle(str, Enum):
  PLAIN = "plain"
  BUBBLE = "bubble"
  LINES = "lines"


class VoiceboxConfig(BaseModel):
  uri: Optional[str] = "ws://localhost:14111/speak"
  api_key: Optional[str] = None
  voice: Optional[str] = None
  speed: Optional[float] = None


class MemoryConfig(BaseModel):
  knowledgebase: Optional[str] = "knowledge"
  max_knowledgebase_results: Optional[int] = 30
  min_relevance_cutoff: Optional[float] = 0.02
  embedding_dimensions: Optional[int] = 1024


class ToolConfig(BaseModel):
  key: str
  params: Dict[str, Any] = Field(default_factory=dict)


class ConnectorConfig(BaseModel):
  name: str
  url: Optional[str] = None
  key: Optional[str] = None
  project_id: Optional[str] = None
  region: Optional[str] = None


class PromptsConfig(BaseModel):
  kalle_system_prompt: Optional[str] = None
  base_tool_prompt: Optional[str] = None


class KalleConfig(BaseSettings):
  model_config = SettingsConfigDict(
      env_prefix="KALLE_",
      case_sensitive=False,
      env_file=".env",
      env_file_encoding="utf-8",
      yaml_file=None,
      extra="forbid",
  )

  data_dir: Optional[str] = None

  cache_dir: Optional[str] = None

  patterns_dir: Optional[str] = None

  format_output: Optional[bool] = False

  smart_tool_selection: bool = True

  default_conversation: Optional[str] = None

  interactive_style: InteractiveStyle = InteractiveStyle.PLAIN

  profiles: Dict[str, Profile] = Field(default_factory=dict)

  models_map: Dict[str, Dict[str, ModelConfig]] = Field(default_factory=dict)

  prompts: PromptsConfig = Field(default_factory=PromptsConfig)

  tools: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

  memory: Optional[MemoryConfig] = None

  voicebox: Optional[VoiceboxConfig] = None

  patterns: Optional[dict] = None

  @model_validator(mode="after")
  def populate_keys(self):
    """Populate the key fields in ModelConfig and ProfileConfig based on their dict keys"""
    # Populate model keys
    if self.models_map:
      for provider_name, models in self.models_map.items():
        for model_key, model_config in models.items():
          if model_config.key is None:
            model_config.key = model_key

    # Populate profile keys
    if self.profiles:
      for profile_key, profile_config in self.profiles.items():
        if profile_config.key is None:
          profile_config.key = profile_key

    return self

  @classmethod
  def settings_customise_sources(
      cls,
      settings_cls: type[BaseSettings],
      init_settings: PydanticBaseSettingsSource,
      env_settings: PydanticBaseSettingsSource,
      dotenv_settings: PydanticBaseSettingsSource,
      file_secret_settings: PydanticBaseSettingsSource,
  ):
    from pydantic_settings.sources import YamlConfigSettingsSource

    config_file = os.getenv("KALLE_CONFIG")
    if config_file:
      # Check if the YAML file exists and is valid
      if not os.path.exists(config_file):
        raise FileNotFoundError(f"YAML config file not found: {config_file}")

      try:
        with open(config_file, "r") as f:
          yaml.safe_load(f)
      except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file {config_file}: {e}")

      yaml_source = YamlConfigSettingsSource(settings_cls, yaml_file=config_file)
      sources = (init_settings, yaml_source, env_settings, dotenv_settings, file_secret_settings)
    else:
      sources = (init_settings, env_settings, dotenv_settings, file_secret_settings)

    return sources
