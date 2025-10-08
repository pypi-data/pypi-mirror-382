# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import sys
import re
import json
import importlib
import inspect

from typing import Optional, Tuple
from rich.console import Console, Group
from rich.panel import Panel
from rich.syntax import Syntax
from rich.status import Status

from kalle.lib.tools.Tool import Tool
from kalle.lib.util.ConfigManager import ConfigManager


class ToolHandler:

  def __init__(
      self,
      config_manager: ConfigManager,
      /,
      base_file_dir: str,
      tool_list: Optional[list[str]] = None,
      console_stderr: Optional[Console] = None,
      rich_status: Optional[Status] = None,
  ):
    self.config_manager = config_manager
    self.base_file_dir = base_file_dir
    self.console_stderr = console_stderr or Console(file=sys.stderr)
    if tool_list == []:
      tool_list = None
    self.tool_list = tool_list
    self.tools = {}
    self.rich_status = rich_status

    self.set_tools(tool_list)

  # register the tool for use
  def register_tool(self, tool_name: str, tool):
    if tool_name is not None:
      self.tools[tool_name] = tool

  # return a list of tools
  def get_tools(self):
    return self.tools

  def set_tools(self, tool_list: Optional[list[str]]):
    self.tool_list = tool_list

    self.tools = {}
    tools_dir = os.path.join(os.path.dirname(__file__), "..", "tools")
    for file_name in os.listdir(tools_dir):
      if file_name.endswith(".py") and not file_name.startswith("__") and not file_name.endswith("Base.py"):
        module_name = file_name[:-3]
        module = importlib.import_module(f"kalle.lib.tools.{module_name}")
        for name, obj in inspect.getmembers(module):
          if inspect.isclass(obj) and issubclass(obj, Tool) and obj is not Tool:
            if tool_list is None or (tool_list is not None and obj.key in tool_list):
              if obj.active:
                self.register_tool(obj.key, obj(self.config_manager, self.base_file_dir))

  # invoke the tool
  async def invoke_tool(self, tool_name, data) -> Tuple[str, str]:
    if self.config_manager.debug:
      self.console_stderr.print(Panel(f"[magenta]{tool_name}", title="[bold magenta]INVOKING TOOL", style="magenta"))

    if tool_name not in self.tools:
      raise ValueError(f"Unsupported Tool: {tool_name}")

    if not self.tools[tool_name].active:
      if self.config_manager.debug:
        self.console_stderr.print(
            Panel(f"[magenta]{tool_name}", title="[bold magenta]Tool is inactive", style="magenta")
        )

        return f"{tool_name} is inactive", "text"

    success, resp, syntax = await self.tools[tool_name].invoke(data)
    if success:
      return resp, syntax

    raise Exception(f"Could not invoke tool: {tool_name} ({resp})")

  def extract_function_contents(self, text):
    pattern = r"<function=([^>]+)>(.*?)</function>"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

  def extract_body_contents(self, text):
    pattern = r"<body_contents=([^>]+)>(.*?)(?:</body_contents|$)"
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

  def preprocess(self, text):
    if self.config_manager.debug:
      self.console_stderr.rule("[bold magenta]Reviewing initial LLM response for tool calls", style="magenta")

    bodies = self.extract_body_contents(text)
    functions = self.extract_function_contents(text)

    body = {}
    for b in bodies:
      body[b[0]] = b[1].strip()
      # remove any wrapping ``` that some models insist on adding (ex: Gemma3)`
      pattern = r"```[^\n\r ]*[\n\r](.*?)```"
      body[b[0]] = re.sub(pattern, r"\1", body[b[0]], flags=re.DOTALL)

    resp = ""
    approved_functions = []
    confirm_functions = []
    for f in functions:
      func_name = f[0]
      params_string = re.sub(r"\\'", "'", f[1])
      try:
        params = json.loads(params_string)
      except json.JSONDecodeError:
        if self.config_manager.debug:
          self.console_stderr.print(
              f"[red]Could not parse params string for tool call function string for {func_name}: {params_string}"
          )
        continue

      if "body_ref" in params and params["body_ref"] in body:
        params["body_contents"] = body[params["body_ref"]]

      if self.tools[func_name].confirm:
        confirm_functions.append(f)
      else:
        approved_functions.append(f)

      for f in confirm_functions:
        tool_name = f[0]
        data = f[1]
        confirmation = False
        if self.tools[tool_name].confirm:
          self.console_stderr.print(
              Panel(f"[yellow]{data}", title=f"[bold yellow]Confirm tool call: {tool_name}", style="yellow")
          )

          from rich.prompt import Prompt
          # wait for confirm
          confirmation = Prompt.ask("[yellow][bold]Confirm? (y/n)[/bold]", default="y")

          if confirmation.lower() == "y":
            approved_functions.append(f)

      if self.config_manager.debug:
        self.console_stderr.print(
            Panel(json.dumps(approved_functions, indent=4), title="[bold magenta]Confirmed functions", style="magenta")
        )

      self.console_stderr.print()

    return approved_functions, bodies

  async def process(self, functions, bodies):
    if self.config_manager.debug:
      self.console_stderr.rule("[bold magenta]Processing tool calls", style="magenta")

    body = {}
    for b in bodies:
      body[b[0]] = b[1].strip()
      # remove any wrapping ``` that some models insist on adding (ex: Gemma3)`
      pattern = r"```[^\n\r ]*[\n\r](.*?)```"
      body[b[0]] = re.sub(pattern, r"\1", body[b[0]], flags=re.DOTALL)

    resp = ""
    function_responses = []
    for f in functions:
      func_name = f[0]
      params_string = re.sub(r"\\'", "'", f[1])
      params = json.loads(params_string)

      if "body_ref" in params and params["body_ref"] in body:
        params["body_contents"] = body[params["body_ref"]]

      try:
        r, syntax = await self.invoke_tool(func_name, params)
        function_responses.append({"name": func_name, "response": r, "syntax": syntax})
        resp += f"---\nTOOL_CALL_RESULT({func_name}): {r}\n"
      except Exception as e:
        if self.config_manager.debug:
          self.console_stderr.print("[red]EXCEPTION")
          self.console_stderr.print("[red]  ERROR: ", type(e).__name__, e)
          self.console_stderr.print_exception(show_locals=True)
        resp += f"Report to the user that there was an internal issue invoking a tool ({func_name} {e}) and ask the user to try again. Don't make any promises.\n"

    if self.config_manager.debug:
      self.console_stderr.rule(style="magenta")
      formatted_function_responses = []
      for r in function_responses:
        formatted_function_responses.append(
            Panel(
                Group("[bold magenta]Result:[/bold magenta]", Syntax(str(r["response"]), r["syntax"])),
                title=f"[bold]{r['name']}",
            )
        )

      self.console_stderr.print(
          Panel(Group(*formatted_function_responses), title="[bold magenta]PROCESSING RESPONSE", style="magenta")
      )

      self.console_stderr.print()

    return resp
