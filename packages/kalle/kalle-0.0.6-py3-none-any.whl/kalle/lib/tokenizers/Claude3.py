# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import anthropic

from . import BaseTokenizer


class Claude3(BaseTokenizer.BaseTokenizer):

  def __init__(self, config: dict, model: str):
    super().__init__(config)
    self.model: str = model
    self.client = anthropic.Anthropic(api_key=self.config["api_key"])

  def get_conversation_tokens(self, conversation: list[dict]):
    system = ""
    if conversation[0]["role"] == "system":
      system = conversation[0]["content"]
      conversation = conversation[1:]

    if len(conversation) == 0:
      conversation = [{"role": "user", "content": "zz"}]

    resp = self.client.messages.count_tokens(
        model=self.model,
        system=system,
        messages=conversation,  # type: ignore
    )

    return resp.input_tokens
