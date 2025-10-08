# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2

from pydantic import BaseModel
from typing import Optional

from kalle.domain.PromptTemplate import PromptTemplate
from kalle.domain.Profile import Profile
from kalle.domain.Constrainer import Constrainer


class Pattern(BaseModel):
  key: str | None = None
  name: Optional[str] = None
  system_prompt_template: Optional[PromptTemplate] = None
  prompt_template: Optional[PromptTemplate] = None
  tools: Optional[list[str]] = None
  constrainer: Optional[Constrainer] = None
  profile: Optional[Profile] = None
