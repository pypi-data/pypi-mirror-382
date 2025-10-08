# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from pydantic import BaseModel
from enum import Enum


class ConstrainerType(str, Enum):
  REGEX = "regex"
  JSONSCHEMA = "jsonschema"
  GBNF = "gbnf"


class Constrainer(BaseModel):
  type: ConstrainerType
  value: str
