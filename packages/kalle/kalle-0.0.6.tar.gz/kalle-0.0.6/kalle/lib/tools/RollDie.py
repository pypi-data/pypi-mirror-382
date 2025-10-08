# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import random

from kalle.lib.util.ConfigManager import ConfigManager
from . import Tool
from typing import Tuple


class RollDie(Tool.Tool):
  key: str = "roll_die"
  confirm: bool = False
  active: bool = True

  def __init__(self, config_manager: ConfigManager, base_file_dir):
    super().__init__(config_manager)
    self.base_file_dir = os.path.abspath(base_file_dir)

  def get_prompt(self):
    return f"""Use the function 'roll_die' to roll a die with a specified number of sides. There are no body elemenents in this request. Anything you would want to say to the user, should be placed into the tool call.

    {self.get_tool_definition()}
    """

  def get_tool_definition(self):
    return """
{{
    "type": "function",
    "function": {{
        "name": "roll_die",
        "description": "Roll a die with a specified number of sides",
        "parameters": {{
            "type": "object",
            "properties": {{
                "sides": {{
                    "type": "integer",
                    "description": "Number of sides on the die"
                }},
                "rolls": {{
                    "type": "integer",
                    "description": "Number of times to roll the die"
                }}
            }},
            "required": ["sides", "rolls"]
        }}
    }}
}}
"""

  def roll_die(self, sides) -> int:
    return random.randint(1, sides)

  async def invoke(self, data: dict) -> Tuple[bool, str, str]:
    sides = 20
    rolls = 1

    if "sides" in data:
      sides = data["sides"]
    if "rolls" in data:
      rolls = data["rolls"]

    results = [self.roll_die(sides) for _ in range(rolls)]
    output = "\n".join([f"d({sides})\troll {i}: {result}" for i, result in enumerate(results, start=1)])

    return (True, f"ONLY RESPOND TO THE USER WITH THE FOLLOWING TEXT:\\n{output}", "text")
