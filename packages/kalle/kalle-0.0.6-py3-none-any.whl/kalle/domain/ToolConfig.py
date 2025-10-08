# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from pydantic import BaseModel
from typing import List


class ToolConfig(BaseModel):
  key: str
  class_path: str


class ToolsList(BaseModel):
  tools: List[ToolConfig]
