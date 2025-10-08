# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC

from pydantic import BaseModel
from typing import Dict, Optional, Any
from enum import Enum


class ModelLocationType(str, Enum):
  LOCAL = "local"
  API = "api"


class ModelParams(BaseModel):
  temperature: Optional[float] = None
  seed: Optional[int] = None
  extra_body: Optional[Dict[str, Any]] = None


class ModelConfig(BaseModel):
  key: Optional[str] = None
  name: Optional[str] = None
  type: str
  location: str
  model: Optional[str] = None
  tokenizer: Optional[str] = None
  context_size: Optional[int] = None
  path: Optional[str] = None
  repo_id: Optional[str] = None
  filename: Optional[str] = None
  publisher: Optional[str] = None
  params: Optional[Dict[str, Any]] = None
