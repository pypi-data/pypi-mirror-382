# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC

from pydantic import BaseModel
from typing import Any, Dict, Optional

from kalle.domain.Constrainer import Constrainer


class Context(BaseModel):
  base_file_dir: str
  use_conversation_history: bool = False
  use_memory: bool = False
  long_conversation_handling: Optional[str] = None
  doc_reference: Optional[str] = None
  knowledgebase: Optional[str] = None
  param_content: Optional[str] = None
  piped_content: Optional[str] = None
  constrainer: Optional[Constrainer] = None
  conversation_key: Optional[str] = None
  args_system_prompt: Optional[str] = None
  args_profile_key: Optional[str] = None
  args_pattern_key: Optional[str] = None
  args_model_string: Optional[str] = None
  args_model_params: Optional[Dict[str, Any]] = None
  follow_uris: Optional[str] = None
  use_tools: bool = False
  use_voice: bool = False
  tool_list: Optional[list] = None
  debug: bool = False
