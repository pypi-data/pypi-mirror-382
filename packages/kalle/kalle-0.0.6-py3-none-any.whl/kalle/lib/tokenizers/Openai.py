# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC

import tiktoken

from . import BaseTokenizer


class Openai(BaseTokenizer.BaseTokenizer):

  def __init__(self, config, model):
    super().__init__(config)
    self.model = model

    self.tokenizer = tiktoken.encoding_for_model(model)

  def tokenize(self, text):
    tokens = self.tokenizer.encode(text)
    return tokens

  def apply_chat_template(self, conversation: list[dict]):
    total_prompt = ""
    for message in conversation:
      if message["role"] == "system":
        total_prompt += f"""<|start_header_id|>system<|end_header_id|>

{ message['content']}<|eot_id|>"""

      if message["role"] == "user":
        total_prompt += f"""<|start_header_id|>user<|end_header_id|>

{ message['content'] }<|eot_id|>"""
      if message["role"] == "assistant":
        total_prompt += f"""<|start_header_id|>assistant<|end_header_id|>

{ message['content'] }<|eot_id|>"""

    return self.tokenize(total_prompt)

  def get_conversation_tokens(self, conversation: list[dict]):
    return len(self.apply_chat_template(conversation))
