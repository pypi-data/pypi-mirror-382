# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import unittest
from kalle.lib.util.Tokenizers import Tokenizers
from kalle.lib.tokenizers.Claude3 import Claude3
from kalle.lib.tokenizers.Openai import Openai
from kalle.lib.tokenizers.Auto import Auto


class TestTokenizers(unittest.TestCase):

  def setUp(self):
    self.config = {"api_key": "not_a_real_key"}
    self.tokenizers = Tokenizers(self.config)

  def test_init(self):
    self.assertIsInstance(self.tokenizers, Tokenizers)
    self.assertEqual(self.tokenizers.config, self.config)

  def test_get_tokenizer(self):

    properties_to_test = [
        ("openai", "gpt-4o", Openai),
        ("claude3", "claude-3-opus-20240229", Claude3),
        ("llama3_1", "llama3_1_70b", Auto),
    ]

    for name, model, tokenizer_class in properties_to_test:
      with self.subTest(name=name, tokenizer_class=tokenizer_class):
        tokenizer = self.tokenizers.get_tokenizer(name, model)
        self.assertIsInstance(tokenizer, tokenizer_class)
        self.assertEqual(tokenizer.config, self.config)

  def test_get_tokenizer_invalid(self):
    with self.assertRaises(Exception):
      self.tokenizers.get_tokenizer("notvalid", "badmodel")

  def test_get_tokenizer_cached(self):
    tokenizer = self.tokenizers.get_tokenizer("llama3", "llama3_8b")
    self.assertIsInstance(tokenizer, Auto)

    tokenizer2 = self.tokenizers.get_tokenizer("llama3", "llama3_8b")
    self.assertEqual(tokenizer, tokenizer2)


if __name__ == "__main__":
  unittest.main()
