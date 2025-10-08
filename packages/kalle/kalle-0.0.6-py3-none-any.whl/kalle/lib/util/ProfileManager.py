# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import sys

from rich.console import Console
from kalle.lib.util.LLMConnectors import LLMConnectors
from kalle.lib.connectors.LLMConnector import LLMConnector
from kalle.lib.tokenizers.BaseTokenizer import BaseTokenizer

from kalle.domain.Profile import Profile
from kalle.domain.ModelConfig import ModelConfig


class ProfileManager:

  def __init__(
      self, config_manager, profile_key, /, model_string: str | None = None, console_stderr: Console | None = None
  ):
    self._config_manager = config_manager
    self.console_stderr = console_stderr or Console(file=sys.stderr)
    self._profile = self._config_manager.config.profiles[profile_key]

    if model_string is not None:
      self._profile.model = model_string

    self._connector = LLMConnectors(self._config_manager, console_stderr=self.console_stderr).get_connector(
        self._profile
    )

  @property
  def profile(self) -> Profile:
    return self._profile

  @property
  def connector(self) -> LLMConnector:
    return self._connector

  @property
  def model(self) -> ModelConfig:
    return self._connector.get_model()  # if self._connector is not None else None

  @property
  def tokenizer(self) -> BaseTokenizer:
    return self._connector.get_tokenizer(self.model.key)
