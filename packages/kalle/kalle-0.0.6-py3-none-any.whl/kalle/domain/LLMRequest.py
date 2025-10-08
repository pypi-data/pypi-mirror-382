# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from pydantic import BaseModel
from typing import Optional

from kalle.domain.ModelConfig import ModelConfig
from kalle.domain.Prompt import Prompt
from kalle.domain.ToolConfig import ToolsList
from kalle.domain.Constrainer import Constrainer
from kalle.domain.Connector import Connector


class LLMRequest(BaseModel):
  key: str
  system_prompt: Optional[Prompt] = None
  piped_prompt: Optional[str] = None
  args_prompt: Optional[str] = None
  tools: Optional[ToolsList] = None
  constrainer: Optional[Constrainer] = None
  connector: Optional[Connector] = None
  model: Optional[ModelConfig] = None
