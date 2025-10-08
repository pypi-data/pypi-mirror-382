# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import datetime
import os
from typing import Tuple

from kalle.lib.util.ConfigManager import ConfigManager
from . import Tool


class UpdateFile(Tool.Tool):
  key: str = "update_file"
  confirm: bool = False
  active: bool = True

  def __init__(self, config_manager: ConfigManager, base_file_dir):
    super().__init__(config_manager)
    self.base_file_dir = os.path.abspath(base_file_dir)

  def get_prompt(self):
    return f"""Use the function 'update_file' to create, make, change or update a file with requested changes.
    ONLY update a given file ONCE.

    Place the file contents into the following form:
    <body_contents=body_ref_id>contents here</body_contents>

    NEVER PROVIDE PLACEHOLDERS AND INSTEAD USE 100% OF THE CONTENT THAT NEEDS TO EXIST IN THE FILE!!!

    {self.get_tool_definition()}
    """

  def get_tool_definition(self):
    return """
{
    "type": "function",
    "function": {
        "name": "update_file",
        "description": "Create, make, change or update the specified file with the new contents",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the file, e.g., example/path/to/the/file.txt"
                },
                "body_ref": {
                    "type": "string",
                    "description": "The reference id to the associated body tag."
                },
                "required": ["path", "body_ref"]
            }
        }
    }
}
"""

  async def invoke(self, data) -> Tuple[bool, str, str]:
    path = None
    body = None

    if "path" in data:
      path = data["path"]

    if "body_contents" in data:
      body = data["body_contents"]

    # Create a backup of the file before updating
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    response = ""
    file_change_type = "created"
    self.base_file_dir = os.path.abspath(self.base_file_dir)

    final_file_path: str = str(path)
    if not final_file_path.startswith("/"):
      final_file_path = os.path.join(self.base_file_dir, str(path))

    backup_path = f"{final_file_path}.bak_{timestamp}"

    try:
      if os.path.exists(f"{final_file_path}"):
        if os.path.exists(f"{backup_path}"):
          return False, f"Report to the user: Backup file already exists: {backup_path}", "text"
        os.replace(final_file_path, backup_path)
        file_change_type = "updated"
        response += f"Report to the user: Existing file backed up as '{backup_path}'\n"
      dir_path = os.path.dirname(final_file_path)  # type: ignore
      if not os.path.exists(dir_path):
        os.makedirs(dir_path)

      with open(final_file_path, "w") as f:
        f.write(body or "")
      if os.path.exists(f"{final_file_path}"):
        if file_change_type == "updated":
          os.chmod(final_file_path, os.stat(backup_path).st_mode)
        response += f"Report to the user: File '{path}' {file_change_type}\n"
        self.console_stderr.print(f"[red]{file_change_type.upper()}: {path}\n")
        return True, response, "text"

      return False, f"Updated file not found: {final_file_path}", "text"
    except Exception as e:
      if self.config_manager.debug:
        self.console_stderr.print_exception(show_locals=True)
      return False, f"Report to the user: An error occurred while writing to '{path}': {e}\n", "text"
