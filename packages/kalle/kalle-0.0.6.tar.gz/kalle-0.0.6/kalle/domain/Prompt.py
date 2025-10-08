# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC

from pydantic import BaseModel
from typing import Optional


class Prompt(BaseModel):
  key: str | None = None
  value: Optional[str] = None
