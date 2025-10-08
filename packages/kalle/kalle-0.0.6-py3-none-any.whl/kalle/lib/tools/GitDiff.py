# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from kalle.lib.util.ConfigManager import ConfigManager
from . import Tool
import subprocess

from rich.console import Group
from rich.panel import Panel
from rich.syntax import Syntax


class GitDiff(Tool.Tool):
  key: str = "git_diff"
  confirm: bool = False
  active: bool = True

  def __init__(self, config_manager: ConfigManager, base_file_dir):
    super().__init__(config_manager)
    self.base_file_dir = base_file_dir

  def get_prompt(self):
    return f"""Use the function 'git_diff' to generate a diff of the current checked out branch in a git repository.
    Don't use --stat or --name-only

    {self.get_tool_definition()}
    """

  def get_tool_definition(self):
    return """
{
    "type": "function",
    "function": {
        "name": "git_diff",
        "description": "Generate the git diff for the current checked out branch in a git repository.",
        "parameters": {
            "type": "object",
            "properties": {
                "flags": {
                    "type": "string",
                    "description": "Flags to pass to 'git diff'"
                },
                "required": ["flags"]
            }
        }
    }
}
"""

  async def invoke(self, data):
    flags = data["flags"].split(" ")

    output = subprocess.check_output(["git", "diff"] + flags).decode("utf-8")

    if self.config_manager.debug:
      self.console_stderr.print()
      self.console_stderr.print(
          Panel(
              Group(
                  f"[magenta]git diff flags: {flags}",
                  Syntax(output, "diff"),
              ),
              title="[bold magenta]GitDiff Debug",
              style="magenta",
          )
      )

      self.console_stderr.print()

    return True, output, "diff"
