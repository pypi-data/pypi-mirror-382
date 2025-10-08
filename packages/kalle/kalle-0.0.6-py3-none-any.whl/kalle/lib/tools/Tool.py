# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import sys
from rich.console import Console
from typing import Tuple

from kalle.lib.util.ConfigManager import ConfigManager


class Tool:
  key: str = "_tool"
  confirm: bool = False
  active: bool = False

  def __init__(self, config_manager: ConfigManager, *args, **kwargs):
    self.config_manager = config_manager
    self.console_stderr = Console(file=sys.stderr)

  def name(self) -> str:
    raise NotImplementedError("Subclasses must implement name method")

  def get_prompt(self) -> str:
    raise NotImplementedError("Subclasses must implement get_prompt method")

  def get_tool_definition(self) -> str:
    raise NotImplementedError("Subclasses must implement get_tool_definition method")

  async def invoke(self, *args, **kwargs) -> Tuple[bool, str, str]:
    raise NotImplementedError("Subclasses must implement invoke method")
