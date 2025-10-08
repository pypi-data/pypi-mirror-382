# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from kalle.lib.tokenizers.BaseTokenizer import BaseTokenizer


class Tokenizers:

  def __init__(self, config):
    self.config = config
    self.llm_tokenizers = {}

  def get_tokenizer(self, tokenizer_key, model) -> BaseTokenizer:
    if tokenizer_key in self.llm_tokenizers:
      return self.llm_tokenizers[tokenizer_key]

    if tokenizer_key == "openai":
      from kalle.lib.tokenizers.Openai import Openai

      self.llm_tokenizers[tokenizer_key] = Openai(self.config, model)

    elif tokenizer_key == "claude3":
      from kalle.lib.tokenizers.Claude3 import Claude3

      self.llm_tokenizers[tokenizer_key] = Claude3(self.config, model)

    else:
      from kalle.lib.tokenizers.Auto import Auto

      self.llm_tokenizers[tokenizer_key] = Auto(self.config, model, tokenizer_key)

    return self.llm_tokenizers[tokenizer_key]
