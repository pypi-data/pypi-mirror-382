# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from pydantic import BaseModel
from typing import Optional


class Uri(BaseModel):
  uri: str
  placeholder: Optional[str] = None
  error: Optional[str] = None
  mime_type: Optional[str] = None
  raw_content: Optional[str] = None
  content_filter: Optional[str] = None
