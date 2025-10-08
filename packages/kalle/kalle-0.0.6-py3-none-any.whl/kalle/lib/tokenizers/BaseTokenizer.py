# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os

from transformers.utils import logging


class BaseTokenizer:

  def __init__(self, config: dict):
    self.config = config
    # We need to set verbosity to error because the autotokenizer line generates this error after a recent upgrade
    # of fastembed:
    # "Special tokens have been added in the vocabulary, make sure the associated word embeddings are fine-tuned or trained."
    # @TODO determine if the warning is material for our use case
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    logging.set_verbosity_error()

  def context_size(self, *args, **kwargs) -> int:
    raise NotImplementedError("Subclasses must implement tokens method")

  def tokens(self, *args, **kwargs) -> list:
    raise NotImplementedError("Subclasses must implement tokens method")

  def messages_tokens(self, *args, **kwargs) -> list:
    raise NotImplementedError("Subclasses must implement messages_tokens method")

  def get_conversation_tokens(self, conversation: list[dict]) -> int:
    raise NotImplementedError("Subclasses must implement messages_tokens method")
