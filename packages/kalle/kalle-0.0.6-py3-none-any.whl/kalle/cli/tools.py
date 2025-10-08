from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.util.ToolHandler import ToolHandler


def cli():
  config = ConfigManager("kalle", "fe2", ".")
  tool_handler = ToolHandler(config, ".")

  for t in tool_handler.get_tools():
    print(f"{t}")
