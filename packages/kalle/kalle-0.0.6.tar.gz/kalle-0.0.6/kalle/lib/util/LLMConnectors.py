# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import sys

from rich.console import Console

from kalle.domain.Profile import Profile
from kalle.lib.connectors.LLMConnector import LLMConnector

from kalle.lib.util.ConfigManager import ConfigManager


class LLMConnectors:

  def __init__(self, config_manager: ConfigManager, console_stderr: Console | None = None):
    self.config_manager = config_manager
    self.console_stderr = console_stderr or Console(file=sys.stderr)
    self.connectors = {}

  def get_connector(self, profile: Profile, model_string: str | None = None) -> LLMConnector:
    if profile.connector.name in self.connectors:
      return self.connectors[profile.connector.name]

    if profile.connector.name not in self.config_manager.models_map:
      raise ValueError(f"Connector name '{profile.connector.name}' is missing from the models map")

    models_map = self.config_manager.models_map[profile.connector.name]
    model_map = models_map.get(profile.model, None) if models_map and profile.model else None
    _model_string = model_string or (model_map.model if model_map and model_map.model else profile.model)

    match profile.connector.name:
      case "vllmapi":
        from kalle.lib.connectors.VllmAPIConnector import VllmAPIConnector

        self.connectors[profile.connector.name] = VllmAPIConnector(
            {
                "api_key": self.config_manager.find_api_key(profile.key),
                "url": profile.connector.url,
                "model": _model_string,
                "retry_max": 3,
                "retry_delay": 1.0,
                "retry_exponential_base": 2.0,
                "jitter": True,
            },
            models_map=models_map,
            console_stderr=self.console_stderr,
            debug=self.config_manager.debug,
        )
      case "tabbyapi":
        from kalle.lib.connectors.TabbyAPIConnector import TabbyAPIConnector

        self.connectors[profile.connector.name] = TabbyAPIConnector(
            {
                "api_key": self.config_manager.find_api_key(profile.key),
                "url": profile.connector.url,
                "model": _model_string,
                "retry_max": 3,
                "retry_delay": 1.0,
                "retry_exponential_base": 2.0,
                "jitter": True,
            },
            models_map=models_map,
            console_stderr=self.console_stderr,
            debug=self.config_manager.debug,
        )
      case "ollama":
        from kalle.lib.connectors.OllamaConnector import OllamaConnector

        self.connectors[profile.connector.name] = OllamaConnector(
            {
                "url": profile.connector.url,
                "model": _model_string,
                "retry_max": 1,
                "retry_delay": 1.0,
                "retry_exponential_base": 2.0,
                "jitter": True,
            },
            models_map=models_map,
            console_stderr=self.console_stderr,
            debug=self.config_manager.debug,
        )
      case "llamacpp":
        from kalle.lib.connectors.LlamaCppConnector import LlamaCppConnector

        self.connectors[profile.connector.name] = LlamaCppConnector(
            {
                "model": _model_string,
                "models_dir": os.path.join(self.config_manager.data_dir, "models"),
            },
            models_map=models_map,
            console_stderr=self.console_stderr,
            debug=self.config_manager.debug,
        )
      case "anthropic":
        from kalle.lib.connectors.AnthropicConnector import AnthropicConnector

        self.connectors[profile.connector.name] = AnthropicConnector(
            {
                "api_key": self.config_manager.find_api_key(profile.key),
                "model": _model_string,
                "retry_max": 3,
                "retry_delay": 1.0,
                "retry_exponential_base": 2.0,
                "jitter": True,
            },
            models_map=models_map,
            console_stderr=self.console_stderr,
            debug=self.config_manager.debug,
        )
      case "openai":
        from kalle.lib.connectors.OpenAIConnector import OpenAIConnector

        self.connectors[profile.connector.name] = OpenAIConnector(
            {
                "url": profile.connector.url,
                "api_key": self.config_manager.find_api_key(profile.key),
                "model": _model_string,
                "retry_max": 3,
                "retry_delay": 1.0,
                "retry_exponential_base": 2.0,
                "jitter": True,
            },
            models_map=models_map,
            console_stderr=self.console_stderr,
            debug=self.config_manager.debug,
        )
      case "groq":
        from kalle.lib.connectors.GroqConnector import GroqConnector

        self.connectors[profile.connector.name] = GroqConnector(
            {
                "api_key": self.config_manager.find_api_key(profile.key),
                "model": _model_string,
                "retry_max": 3,
                "retry_delay": 1.0,
                "retry_exponential_base": 2.0,
                "jitter": True,
            },
            models_map=models_map,
            console_stderr=self.console_stderr,
            debug=self.config_manager.debug,
        )
      case "vertexai":
        from kalle.lib.connectors.GoogleVertexAIConnector import GoogleVertexAIConnector

        self.connectors[profile.connector.name] = GoogleVertexAIConnector(
            {
                "api_key": self.config_manager.find_api_key(profile.key),
                "model": _model_string,
                "token_cache_dir": os.path.join(self.config_manager.cache_dir, "tokens"),
                "credentials_path": profile.connector.credentials_path,
                "project_id": profile.connector.project_id,
                "region": profile.connector.region,
                "retry_max": 3,
                "retry_delay": 1.0,
                "retry_exponential_base": 2.0,
                "jitter": True,
            },
            models_map=models_map,
            console_stderr=self.console_stderr,
            debug=self.config_manager.debug,
        )

    return self.connectors[profile.connector.name]
