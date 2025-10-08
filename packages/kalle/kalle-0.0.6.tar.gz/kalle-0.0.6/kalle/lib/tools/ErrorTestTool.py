# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC

from typing import Tuple
from kalle.lib.util.ConfigManager import ConfigManager
from . import Tool


class ErrorTestTool(Tool.Tool):
  key: str = "error_test_tool"
  confirm: bool = False
  active: bool = True

  def __init__(self, config_manager: ConfigManager, base_file_dir):
    super().__init__(config_manager)
    self.base_file_dir = base_file_dir

  def get_prompt(self):
    return f"""DO NOT USE THIS TOOL FOR TESTING ONLY:

    {self.get_tool_definition()}
    """

  def get_tool_definition(self):
    return """
{
    "type": "function",
    "function": {
        "name": "error_test_tool"<
        "description": "DO NOT USE THIS TOOL FOR TESTING ONLY",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "COMPLETELY IRRELEVANT TEXT"
                },
                "required": ["text"]
            }
        }
    }
}
"""

  async def invoke(self, data) -> Tuple[bool, str, str]:
    text = data["text"] if "text" in data else None

    raise Exception("Always error")

    if text is not None:
      return True, text, "text"
    return False, "", "text"
