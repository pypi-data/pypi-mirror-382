# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC

from pydantic import BaseModel
from typing import Optional


class PromptTemplate(BaseModel):
  key: str | None = None
  name: Optional[str] = None
  value: Optional[str] = None
