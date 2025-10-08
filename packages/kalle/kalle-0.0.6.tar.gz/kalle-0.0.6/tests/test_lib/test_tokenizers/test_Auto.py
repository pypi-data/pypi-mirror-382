# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import unittest

from kalle.lib.tokenizers.Auto import Auto


class TestTokenizers(unittest.TestCase):

  def setUp(self):
    self.config = {"local_only": False}

  def test_get_tokenizer(self):
    tokenizer = Auto(self.config, "llama3_1_700b", "llama3_1")
    self.assertIsInstance(tokenizer, Auto)

  def test_get_huggingface_tokenizer(self):
    tokenizer = Auto(self.config, "llama3_1_8b", "unsloth/llama-3-8b")
    self.assertIsInstance(tokenizer, Auto)

  def test_get_invalid_huggingface_tokenizer(self):
    with self.assertRaises(ValueError):
      Auto(self.config, "llama3_1_8b", "invalid/llama-3-8b")

  def test_tokenize(self):
    tokenizer = Auto(self.config, "llama3_1_700b", "llama3_1")
    tokens = tokenizer.tokenize("Hello, World!")
    self.assertEqual(tokens, [128000, 9906, 11, 4435, 0])

  def test_tokenize_huggingface_tokenizer(self):
    tokenizer = Auto(self.config, "smollm2_1_7b", "HuggingFaceTB/SmolLM2-1.7B-Instruct")
    tokens = tokenizer.tokenize("Hello, World!")
    self.assertEqual(tokens, [19556, 28, 2260, 17])

  def test_apply_chat_template(self):
    tokenizer = Auto(self.config, "llama3_1_700b", "llama3_1")
    conversation = [
        {"role": "system", "content": "This is a system message"},
        {"role": "user", "content": "This is a user message"},
        {"role": "assistant", "content": "This is an assistant message"},
    ]
    tokens = tokenizer.apply_chat_template(conversation)
    self.assertEqual(len(tokens), 31)

  def test_get_conversation_tokens(self):
    tokenizer = Auto(self.config, "llama3_1_700b", "llama3_1")
    conversation = [
        {"role": "system", "content": "This is a system message"},
        {"role": "user", "content": "This is a user message"},
        {"role": "assistant", "content": "This is an assistant message"},
    ]
    num_tokens = tokenizer.get_conversation_tokens(conversation)
    self.assertEqual(num_tokens, 31)


if __name__ == "__main__":
  unittest.main()
