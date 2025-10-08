# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from __future__ import annotations
import os
import yaml
import sys
import argparse
from collections.abc import Iterable

from textual import on
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, VerticalGroup, Horizontal
from textual.widgets import Label, Input, Button, TextArea, Footer, Header, Static, DirectoryTree, Select, SelectionList
from textual.reactive import reactive
from textual.screen import Screen
from textual.events import Key

from pathlib import Path


from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.util.ToolHandler import ToolHandler

parser = argparse.ArgumentParser(
    description="Pattern Editor",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument("--dir", type=str, default=".", help="Base dir for files")
parser.add_argument("args", nargs=argparse.REMAINDER, help="The file to edit")

args = parser.parse_args()
base_dir = args.dir

config_manager = ConfigManager(
    "kalle", "fe2", conversation_key=None, base_file_dir=base_dir, use_memory=False, debug=False
)

file_path = ""
if len(args.args) > 0:
  file_path = args.args[0]

  if not str(file_path).endswith(".yaml"):
    file_path += ".yaml"

  file_path = os.path.join(config_manager.patterns_dir, file_path)


class Editor(VerticalGroup):
  active_file_path = reactive("None")

  def __init__(self, file_path: str | None = None) -> None:
    self.file_path = file_path
    self.tool_handler = ToolHandler(config_manager, base_dir)
    super().__init__()

  def on_mount(self) -> None:
    if self.file_path is not None:
      self.load_file(Path(self.file_path))

  def compose(self) -> ComposeResult:
    self.path_input = Input(id="path")
    self.path_input.styles.width = "100%"
    self.path_input.styles.border = ("solid", "ansi_white")
    self.path_input.border_title = "Pattern File Path"

    self.name_input = Input(id="name", placeholder="Pattern Name")
    self.name_input.styles.width = "100%"
    self.name_input.styles.border = ("solid", "ansi_white")
    self.name_input.border_title = "Name"
    self.notes_textarea = TextArea(id="notes", text="", language="markdown")
    self.notes_textarea.styles.width = "100%"
    self.notes_textarea.styles.height = "auto"
    self.notes_textarea.styles.border = ("solid", "ansi_white")
    self.notes_textarea.border_title = "Notes"

    self.system_prompt_template_textarea = TextArea(id="system_prompt_template", text="", language="markdown")
    self.system_prompt_template_textarea.styles.width = "100%"
    self.system_prompt_template_textarea.styles.height = "auto"
    self.system_prompt_template_textarea.styles.border = ("solid", "ansi_white")
    self.system_prompt_template_textarea.border_title = "System Prompt Template"

    self.prompt_template_textarea = TextArea(id="prompt_template", text="", language="markdown")
    self.prompt_template_textarea.styles.width = "100%"
    self.prompt_template_textarea.styles.height = "auto"
    self.prompt_template_textarea.styles.border = ("solid", "ansi_white")
    self.prompt_template_textarea.border_title = "Prompt Template"

    constrainer_types = [
        ("regex", "regex"),
        ("jsonschema", "jsonschema"),
        ("gbnf", "gbnf"),
    ]
    self.constrainer_type = Select(options=constrainer_types, id="constrainer_type")
    self.constrainer_type.styles.border = ("none", "black")
    self.constrainer_value = TextArea(id="constrainer_value")
    self.constrainer_value.styles.height = "auto"
    self.constrainer_value.styles.border = ("solid", "ansi_white")
    self.constrainer_value.border_title = "Constrainer Value"
    self.constrainer = VerticalGroup(
        self.constrainer_type,
        self.constrainer_value,
    )
    self.constrainer.styles.border = ("solid", "ansi_white")
    self.constrainer.border_title = "Constrainer"

    tools = self.tool_handler.get_tools().keys()
    tool_options = []
    for t in tools:
      tool_options.append((t, t))

    self.tools = SelectionList[str](*tool_options, id="tools")
    self.tools.styles.width = "100%"
    self.tools.styles.border = ("solid", "ansi_white")
    self.tooltborder_title = "Tools"

    profile_options = []
    for i, k in enumerate(config_manager.config.profiles.keys()):
      profile_options.append((k, k))

    self.profile = Select(options=profile_options, id="profile")
    self.profile.styles.width = "100%"
    self.profile.styles.border = ("solid", "ansi_white")
    self.profile.border_title = "Profile"

    yield VerticalScroll(
        self.path_input,
        self.name_input,
        self.notes_textarea,
        self.system_prompt_template_textarea,
        self.prompt_template_textarea,
        self.constrainer,
        self.tools,
        self.profile,
    )

    self.buttons = Horizontal(
        Button("New", id="new", variant="primary"),
        Label(" "),
        Button("Load", id="load", variant="primary"),
        Label(" "),
        Button("Save", id="save", variant="primary"),
        Label(" "),
        Button("Quit", id="quit", variant="primary"),
    )
    self.buttons.styles.height = "3"
    yield self.buttons

  def new_file(self) -> None:
    self.file_path = None

    self.query_one("#path").value = ""
    self.query_one("#path").disabled = False
    self.query_one("#path").focus()
    self.query_one("#name").value = ""
    self.query_one("#notes").text = ""
    self.query_one("#system_prompt_template").text = ""
    self.query_one("#prompt_template").text = ""
    self.query_one("#constrainer_type").clear()
    self.query_one("#constrainer_value").text = ""
    self.query_one("#profile").clear()
    self.query_one("#tools").deselect_all()

  def load_file(self, file_path: Path) -> None:
    self.query_one("#path").value = ""
    self.query_one("#name").value = ""
    self.query_one("#notes").text = ""
    self.query_one("#system_prompt_template").text = ""
    self.query_one("#prompt_template").text = ""
    self.query_one("#constrainer_type").clear()
    self.query_one("#constrainer_value").text = ""
    self.query_one("#profile").clear()
    self.query_one("#tools").deselect_all()

    try:
      if file_path is not None and str(file_path) != "" and str(file_path) != ".":
        with open(file_path, "r") as file:
          data = yaml.safe_load(file)
          self.query_one("#path").value = os.path.relpath(str(file_path), base_dir)
          self.query_one("#path").disabled = True
          self.query_one("#name").value = data.get("name", "") or ""
          self.query_one("#notes").text = data.get("notes", "") or ""
          self.query_one("#system_prompt_template").text = data.get("system_prompt_template", "") or ""
          self.query_one("#prompt_template").text = data.get("prompt_template", "") or ""
          if "constrainer" in data and data["constrainer"] is not None and data["constrainer"] != "":
            self.query_one("#constrainer_type").value = data["constrainer"].get("type", "") or ""
            self.query_one("#constrainer_value").text = data["constrainer"].get("value", "") or ""
          if "profile" in data and data["profile"] is not None and data["profile"] != "":
            self.query_one("#profile").value = data.get("profile", "") or ""
          if "tools" in data and data["tools"] is not None and type(data["tools"]) is list:
            tools = self.tool_handler.get_tools().keys()
            selected_tools = data.get("tools")
            for t in tools:
              if t in selected_tools:
                self.query_one("#tools").select(t)

          self.file_path = file_path

          self.notify(f"File loaded: {file_path}")
    except FileNotFoundError:
      self.notify(f"File not found: {file_path}", severity="warning")
    except yaml.YAMLError as e:
      self.notify(f"{e}", title=f"Invalid yaml file: {file_path}", severity="warning")
    except Exception as e:
      self.notify(f"Invalid: {file_path} - {e}", severity="warning")

    if self.file_path is None or self.file_path == "":
      self.path_input.focus()
    else:
      self.name_input.focus()

  def save_file(self) -> None:
    if str(self.file_path) == "" and str(self.path_input.value) == "":
      self.notify("No file to save", severity="error")
      return

    file_path = self.file_path or os.path.join(config_manager.patterns_dir, self.path_input.value)

    if not str(file_path).endswith(".yaml"):
      file_path += ".yaml"

    if (self.file_path is None or self.file_path == "") and os.path.exists(file_path):
      self.notify(f"File {file_path} already exists. Please choose a different name.", severity="error")
      return

    pattern = {
        "name": self.name_input.value,
        "notes": "\n".join([line.rstrip() for line in self.notes_textarea.text.splitlines()]),
        "system_prompt_template": "\n".join(
            [line.rstrip() for line in self.system_prompt_template_textarea.text.splitlines()]
        ),
        "prompt_template": "\n".join([line.rstrip() for line in self.prompt_template_textarea.text.splitlines()]),
        "constrainer": None,
        "tools": None,
        "profile": None,
    }
    if self.constrainer_type.value != Select.BLANK:
      pattern["constrainer"] = {
          "type": self.constrainer_type.value,
          "value": self.constrainer_value.text,
      }

    if self.tools.selected != Select.BLANK:
      pattern["tools"] = self.tools.selected

    if self.profile.value != Select.BLANK:
      pattern["profile"] = self.profile.value

    with open(file_path, "w") as file:
      yaml.dump(pattern, file, default_flow_style=False, indent=4)
      self.notify(f"Pattern: {str(self.name_input.value)} saved to {file_path}!")


class FilteredDirectoryTree(DirectoryTree):

  def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
    return [
        path
        for path in paths
        if (path.name.endswith(".yaml") or os.path.isdir(path.name)) and not path.name.startswith(".")
    ]


class LoadFile(Screen):
  BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

  def compose(self) -> ComposeResult:
    self.screen_title = Static("Load a Pattern")
    self.screen_title.styles.width = "100%"
    self.screen_title.styles.border = ("solid", "ansi_white")
    yield self.screen_title

    self.dir_tree = FilteredDirectoryTree(config_manager.patterns_dir)
    self.dir_tree.styles.border = ("solid", "ansi_white")

    self.dir_tree.border_title = "Files"
    self.dir_tree.focus()
    yield self.dir_tree

    yield Horizontal(
        Button("Cancel", id="cancel", variant="primary"),
    )

  def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "cancel" and self.parent is not None:
      self.parent.app.pop_screen()

  @on(DirectoryTree.FileSelected)
  def handle_file_selected(self, message: DirectoryTree.FileSelected) -> None:
    if self.parent is not None:
      self.parent.app.editor.load_file(message.path)
      self.parent.app.pop_screen()


class PatternEditor(App):
  SCREENS = {"load_file": LoadFile}
  # BINDINGS = [("b", "push_screen('bsod')", "BSOD")]

  def __init__(self, /, base_dir: str | None = None, file_path: str | None = None) -> None:
    self.base_dir = base_dir
    self.file_path = file_path
    super().__init__()

  def compose(self) -> ComposeResult:
    yield Header()
    yield Footer()
    self.editor = Editor(file_path)
    yield self.editor

  def action_toggle_dark(self) -> None:
    self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

  def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "new":
      self.editor.new_file()
    if event.button.id == "save":
      self.editor.save_file()
    if event.button.id == "load":
      self.push_screen("load_file")
    if event.button.id == "quit":
      sys.exit(0)

  def on_key(self, event: Key) -> None:
    if event.key == "ctrl+n":
      self.editor.new_file()
    if event.key == "ctrl+s":
      self.editor.save_file()
    if event.key == "ctrl+l":
      self.push_screen("load_file")
    if event.key == "ctrl+q":
      sys.exit(0)


def cli():
  app = PatternEditor(base_dir=base_dir, file_path=os.path.join(base_dir, file_path))
  app.run()


if __name__ == "__main__":
  cli()
