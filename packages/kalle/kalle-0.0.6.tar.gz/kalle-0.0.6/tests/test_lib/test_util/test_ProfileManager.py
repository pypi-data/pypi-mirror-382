# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import unittest
from kalle.domain.ModelConfig import ModelConfig
from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.util.ProfileManager import ProfileManager
from kalle.lib.connectors.LLMConnector import LLMConnector
from kalle.lib.connectors.LlamaCppConnector import LlamaCppConnector
from kalle.lib.tokenizers.Auto import Auto
from kalle.domain.Profile import Profile


class TestProfileManager(unittest.TestCase):

  def setUp(self):
    appname = "kalle"
    appauthor = "fe2"
    self.fixtures_dir = os.path.join(os.path.dirname(__file__), "../../fixtures")
    self.config_file = os.path.join(self.fixtures_dir, "config.yml")
    os.environ["KALLE_CONFIG"] = self.config_file
    self.config = ConfigManager(
        appname, appauthor, conversation_key="default", base_file_dir=self.fixtures_dir, use_conversation_history=False
    )

  def test_init(self):
    profile_manager = ProfileManager(self.config, "base")
    self.assertEqual(profile_manager._config_manager, self.config)
    self.assertIsInstance(profile_manager._profile, Profile)
    self.assertIsInstance(profile_manager._connector, LLMConnector)

  def test_init_with_model(self):
    profile_manager = ProfileManager(self.config, "base", "smollm2_1.7b_instruct")
    self.assertEqual(profile_manager._config_manager, self.config)
    self.assertIsInstance(profile_manager._profile, Profile)
    self.assertIsInstance(profile_manager._connector, LLMConnector)

  def test_profile(self):
    profile_manager = ProfileManager(self.config, "base")
    self.assertIsInstance(profile_manager.profile, Profile)

  def test_model(self):
    profile_manager = ProfileManager(self.config, "base")
    self.assertIsInstance(profile_manager.model, ModelConfig)

  def test_connector(self):
    profile_manager = ProfileManager(self.config, "base")
    self.assertIsInstance(profile_manager.connector, LlamaCppConnector)

  def test_tokenizer(self):
    profile_manager = ProfileManager(self.config, "base")
    self.assertIsInstance(profile_manager.tokenizer, Auto)


if __name__ == "__main__":
  unittest.main()
