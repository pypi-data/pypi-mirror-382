# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC

from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

from kalle.domain.Connector import Connector


class Profile(BaseModel):
  connector: Connector
  key: Optional[str] = None
  name: Optional[str] = None
  model: Optional[str] = None
  model_params: Optional[Dict[str, Any]] = Field(default=None)
