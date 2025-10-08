# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from __future__ import annotations
import os
import sys
from collections.abc import Iterable
import argparse
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, VerticalGroup, Horizontal, Container
from textual.widgets import Label, Button, Footer, Header, Static, DirectoryTree, TabbedContent, Markdown, Pretty, Collapsible
from textual.reactive import reactive
from textual.screen import Screen
from textual.content import Content
from textual import on
from textual.events import Key

from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.util.ConversationTools import ConversationTools

from typing import Optional

parser = argparse.ArgumentParser(
    description="Conversation Manager",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)

parser.add_argument("--dir", type=str, help="Base dir for files")
parser.add_argument("args", nargs=argparse.REMAINDER, help="The file to edit")

args = parser.parse_args()
base_dir = args.dir


class Editor(VerticalGroup):
  conversation_file: reactive[str] = reactive("", recompose=True)

  def __init__(self, conversation_key: Optional[str], conversation_file: Optional[str]) -> None:
    self.conversation_key = conversation_key
    self.conversation = None
    super().__init__()
    self.conversation_file = conversation_file

  def on_mount(self) -> None:
    if self.conversation_key is not None and self.parent is not None:
      self.conversation_file = self.parent.app.conversation_file

  def compose(self) -> ComposeResult:
    self.conversation_metadata = VerticalGroup(
        Label("Metadata"),
    )

    self.conversation = VerticalGroup(
        Label("Conversation"),
    )

    self.buttons = Horizontal(
        # Button("New", id="new", variant="primary"),
        # Label(" "),
        Button("Load", id="load", variant="primary"),
        Label(" "),
        # Button("Save", id="save", variant="primary"),
        # Label(" "),
        Button("Quit", id="quit", variant="primary"),
    )
    self.buttons.styles.height = "3"

    if self.parent is None:
      raise Exception("Could not find app")

    app = self.parent.parent

    self.conversation = app.conversation_tools.load_conversation(conversation_file=self.conversation_file)

    with Container(id="app-grid"):
      with Container(id="title"):
        yield Label(f"[bold]Conversation:[/bold] {str(self.conversation_key)}")
        yield Label(f"[bold]File:[/bold] {self.conversation_file}")

      with Container(id="main"):
        with TabbedContent("[bold]Conversation", "[bold]Metadata", id="tabs"):
          with VerticalScroll(id="conversation-tab"):
            cx = []
            for c in self.conversation.conversation:
              with Container() as ci:
                ci.classes = "conversation-item-user"
                if c.role == "assistant":
                  ci.classes = "conversation-item-assistant"
                ci.border_title = c.role
                with Container() as cm:
                  cm.classes = "conversation-item-head"
                  timestamp = datetime.fromtimestamp(c.timestamp or 0)
                  yield Label(f"[bold]Timestamp:[/bold] {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                  lines = c.content.split("\n")

                  if len(lines) > 1:
                    line = lines[0]

                    if len(line) > 200:
                      line = line[:200]

                    lines = [line] + ["***...continues...***"]
                  cs = Markdown("\n".join(lines))
                  cs.classes = "conversation-item-brief"
                  yield cs

                with Collapsible(collapsed=True, title="[bold]Details") as mc:
                  mc.classes = "conversation-item-collapse"

                  with TabbedContent("[bold]Profile", "[bold]System Prompt") as tc:
                    tc.styles.border = ("solid", "ansi_white")
                    p = Pretty(c.profile)
                    p.classes = "profile-item"
                    yield p
                    yield Markdown(c.system_prompt)

                  with TabbedContent("[bold]Param", "[bold]Piped") as tc:
                    tc.styles.border = ("solid", "ansi_white")
                    tc.border_title = "[bold]Request Content"
                    yield Markdown(c.param_content)
                    yield Markdown(c.piped_content)

                  with TabbedContent(
                      "[bold]Prompt", "[bold]Response", "[bold]Tool Call Results", "[bold]Tooled Request"
                  ) as tc:
                    tc.styles.border = ("solid", "ansi_white")
                    tc.border_title = "[bold]Tool Call Details"
                    yield Markdown(c.tool_prompt)
                    yield Static(Content(c.tool_response or ""))
                    yield Pretty(c.tool_call_results or [])
                    yield Static(Content(c.tooled_request or ""))

                  with TabbedContent("[bold]Markdown", "[bold]Raw") as tc:
                    tc.styles.border = ("solid", "ansi_white")
                    tc.border_title = "[bold]Compiled Request Content"

                    md = Markdown(c.content)
                    md.classes = "conversation-content-markdown"
                    raw = Static(Content(c.content))
                    raw.classes = "conversation-content-raw"

                    yield md
                    yield raw

              cx.append(ci)

            yield VerticalScroll(*cx)

          with Container(id="metadata-tab"):
            version = Label(f"{self.conversation.metadata.version}", id="pretty-version")
            profile = Pretty(self.conversation.metadata.profile, id="pretty-profile")
            system_prompt = Markdown(self.conversation.metadata.system_prompt, id="pretty-system-prompt")
            version.border_title = "[bold]Conversation File Version"
            profile.border_title = "[bold]Current Profile"
            system_prompt.border_title = "[bold]Current System Prompt"
            yield VerticalScroll(
                version,
                profile,
                system_prompt,
            )

      with Container(id="bottom-button-pane"):
        yield self.buttons


class FilteredDirectoryTree(DirectoryTree):

  def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
    return [
        path
        for path in paths
        if (path.name.endswith(".json") or os.path.isdir(path.name)) and not path.name.startswith(".")
    ]


class LoadFile(Screen):
  BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

  def compose(self) -> ComposeResult:
    self.screen_title = Static("[bold]Load Conversation", id="load-conversation-title")
    self.screen_title.styles.width = "100%"
    self.screen_title.styles.border = ("solid", "ansi_white")
    yield self.screen_title

    self.dir_tree = FilteredDirectoryTree(self.parent.app.config.conversation_dir)
    self.dir_tree.styles.border = ("solid", "ansi_white")

    self.dir_tree.border_title = "[bold]Files"
    self.dir_tree.focus()
    yield self.dir_tree

    yield Horizontal(
        Button("Cancel", id="cancel", variant="primary"),
    )

  def on_button_pressed(self, event: Button.Pressed) -> None:
    if event.button.id == "cancel":
      self.app.pop_screen()

  @on(DirectoryTree.FileSelected)
  def handle_file_selected(self, message: DirectoryTree.FileSelected) -> None:
    self.parent.app.editor.conversation_file = os.path.basename(message.path)
    self.parent.app.editor.conversation_key = self.parent.app.editor.conversation_file[:-5]
    self.parent.app.editor.conversation_key = self.parent.app.editor.conversation_key.split(".20")[0]
    # conversation = app.conversation_tools.load_conversation(os.path.join(app.config.conversation_dir, app.editor.conversation_file))
    # app.editor.conversation = conversation.conversation
    self.parent.app.editor.mutate_reactive(Editor.conversation_file)
    self.parent.app.pop_screen()
    self.notify(f"{self.parent.app.editor.conversation_file}", title="Conversation File Loaded")


class ConversationManager(App):
  SCREENS = {"load_file": LoadFile}
  # BINDINGS = [("b", "push_screen('bsod')", "BSOD")]
  CSS_PATH = "conversationmanager_layouts.tcss"

  def __init__(self, /, base_dir: str = None, conversation_key: str = None) -> None:
    self.base_dir = base_dir
    self.config = ConfigManager(
        "kalle", "fe2", conversation_key=conversation_key, base_file_dir=base_dir, use_memory=True, debug=False
    )
    self.conversation_tools = ConversationTools(self.config)
    self.conversation_key = self.config.conversation_key
    self.conversation_file = self.conversation_tools.conversation_file()

    super().__init__()

  def compose(self) -> ComposeResult:
    yield Header()
    yield Footer()
    self.editor = Editor(self.conversation_key, self.conversation_file)
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
  conversation_key = "default"
  if len(args.args) > 0:
    conversation_key = args.args[0]

  app = ConversationManager(conversation_key=conversation_key, base_dir=base_dir)
  app.run()


if __name__ == "__main__":
  cli()
