# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import datetime
import json
import os
import re

from typing import Optional

from kalle.lib.util.ConfigManager import ConfigManager
from kalle.domain.Conversation import Conversation, ConversationMetadata, ConversationMessage


class ConversationTools:

  def __init__(self, config_manager: ConfigManager, /, conversation_key: Optional[str] = None):
    self.config_manager = config_manager
    self.conversation_key = conversation_key or config_manager.conversation_key
    if not os.path.exists(self.config_manager.conversation_dir):
      os.makedirs(self.config_manager.conversation_dir)

  @property
  def empty_conversation(self):
    return Conversation()

  @property
  def conversation_dir(self):
    return self.config_manager.conversation_dir

  def conversation_file(self, conversation_key: Optional[str] = None) -> Optional[str]:
    conversation_key = conversation_key or self.conversation_key
    if conversation_key is not None:
      return os.path.normpath(f"{self.conversation_dir}/conversation_{conversation_key}.json")
    return None

  def list_conversations(self):
    directory = self.conversation_dir
    file_list = os.listdir(directory)
    conversations = [
        re.sub(r"^conversation_", "", re.sub(r"\..*", "", file)) for file in file_list if "conversation" in file
    ]
    conversations = sorted(list(set(conversations)))

    return conversations

  def load_conversation(self, /, conversation_key: Optional[str] = None, conversation_file: Optional[str] = None):
    conversation = self.empty_conversation

    if conversation_key is not None:
      conversation_file = self.conversation_file(conversation_key)

    if conversation_file is not None and os.path.exists(conversation_file):
      with open(conversation_file) as file:
        file_contents = file.read()
        if file_contents is not None and file_contents != "":
          file_contents_objects = json.loads(file_contents)
          if isinstance(file_contents_objects, list):
            # convert to new format
            new_file_contents = Conversation()
            for i in file_contents_objects:
              new_file_contents.conversation.append(
                  ConversationMessage(
                      role=i["role"],
                      content=i["content"],
                  )
              )
            file_contents = new_file_contents.model_dump_json(indent=4)

          if "metadata" in file_contents_objects and isinstance(file_contents_objects["metadata"], dict):
            conversation_metadata = ConversationMetadata(version=file_contents_objects["metadata"]["version"])
            file_contents_objects["metadata"] = conversation_metadata

          conversation = Conversation().model_validate_json(file_contents)

    return conversation

  # persist conversation
  def persist_conversation(self, conversation, /, conversation_key: str | None = None):
    conversation_file = self.conversation_file(conversation_key)

    if conversation_file is not None:
      with open(conversation_file, "w") as file:
        file.write(conversation.model_dump_json(indent=4))

  # archive conversation
  def archive_conversation(self, /, conversation_key: Optional[str] = None) -> bool:
    conversation_file = self.conversation_file(conversation_key) or "INVALID"
    if conversation_file is not None and conversation_file != "INVALID" and os.path.exists(conversation_file):
      now = datetime.datetime.now()
      stime = now.strftime("%Y-%m-%dT%H-%M-%S.%f")
      filename, _ = os.path.splitext(conversation_file)
      archive_file = f"{filename}.{stime}.json"
      os.rename(conversation_file, archive_file)

      conversation = self.empty_conversation
      self.persist_conversation(conversation, conversation_key=conversation_key)
      return True

    return False

  # truncate to the last <count> messages
  def truncate_message_list(self, messages, count=10):
    return messages[-count:]
