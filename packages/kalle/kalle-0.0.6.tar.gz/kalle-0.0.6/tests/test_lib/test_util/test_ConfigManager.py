# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import sys
import unittest

from unittest.mock import patch

from kalle.lib.util.ConfigManager import ConfigManager, find_conversation_key

from kalle.domain.Pattern import Pattern
from kalle.domain.Profile import Profile
from kalle.domain.Connector import Connector
from kalle.domain.PromptTemplate import PromptTemplate
from kalle.domain.Constrainer import Constrainer, ConstrainerType


class TestConfigManager(unittest.TestCase):

  def setUp(self):
    self.appname = "kalle"
    self.appauthor = "fe2"
    self.fixtures_dir = os.path.join(os.path.dirname(__file__), "../../fixtures")
    self.config_file = os.path.join(self.fixtures_dir, "config.yml")
    os.environ["KALLE_CONFIG"] = self.config_file
    self.maxDiff = 1000

  def tearDown(self):
    try:
      self.config_manager = None
    except AttributeError:
      pass

  # @TODO should the path somehow be capped so it doesn't escape the text fixture?
  def test_find_conversation_key(self):
    # Test when .kalle_conversation file is not found
    conversation_key = find_conversation_key(self.fixtures_dir)
    self.assertIsNone(conversation_key)

    # Test when .kalle_conversation file is not found in any parent directories
    conversation_key = find_conversation_key(os.path.join(self.fixtures_dir, "testdir1/testdir1.1/testdir1.1.1/"))
    self.assertIsNone(conversation_key)

    # Test when .kalle_conversation file is found in the specifed directory
    conversation_key = find_conversation_key(os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.2/"))
    self.assertEqual(conversation_key, "testconversation1.2.2")

    # Test when .kalle_conversation file is found in a parent directory
    conversation_key = find_conversation_key(os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.1/"))
    self.assertEqual(conversation_key, "testconversation1.2")

  def test_config_init(self):
    # Test basic init
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")

    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key="default",
        base_file_dir=self.fixtures_dir,
        use_conversation_history=False,
    )
    self.assertIsNotNone(self.config_manager)

    # Test that default is the conversation key
    self.assertEqual(type(self.config_manager), ConfigManager)
    self.assertEqual(os.path.relpath(self.config_manager.config_dir), "tests/fixtures")  # type: ignore
    self.assertEqual(self.config_manager.cache_dir, "tests/fixtures/kalle_cache")
    self.assertEqual(self.config_manager.data_dir, "tests/fixtures/kalle_data")
    self.assertEqual(self.config_manager.format_output, False)
    self.assertEqual(
        self.config_manager.config.tools["google_app"]["credentials_path"], "tests/fixtures/fake_creds.json"
    )
    self.assertEqual(self.config_manager.config.interactive_style, "plain")

  # test the happy path of a good yaml with correct keys
  def test_config_validate_good(self):
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
    )

  # test invalid file ppermissions
  @patch("sys.exit")
  def test_config_validate_invalid_perms(self, mock_exit):
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config_badperms.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
    )
    mock_exit.assert_called_once_with(112)

  # test broken yaml
  @patch("sys.exit")
  def test_config_validate_broken(self, mock_exit):
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config_broken.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
        debug=True,
    )
    mock_exit.assert_called_once_with(110)

  # Test for invalid keys but well structured yaml
  @patch("sys.exit")
  def test_config_validate_invalid(self, mock_exit):
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config_invalid.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
        debug=True,
    )
    mock_exit.assert_called_once_with(110)

  # test that we auto-create the file if it's missing
  def test_config_validate_missing(self):
    config_file = os.path.join(self.fixtures_dir, "config_missing.yml")
    os.environ["KALLE_CONFIG"] = config_file
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
        debug=True,
    )
    self.assertTrue(os.path.exists(os.environ["KALLE_CONFIG"]))
    os.unlink(config_file)

  def test_config_conversation_key_no_conversation_key(self):
    # Test the base case of no passed key and memory (conversation) is in use
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
    )

    # Test that default is the conversation key
    self.assertEqual(self.config_manager.conversation_key, "default")

  def test_config_conversation_key_no_conversation_key_with_configured_default(self):
    # Test the base case of no passed key and memory (conversation) is in use
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config_default_conversation.yml")

    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
    )

    # Test that default is the conversation key
    self.assertEqual(self.config_manager.conversation_key, "defaulttest")

  def test_config_conversation_key(self):
    # Test when a specific conversation_key is provided
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key="someconversation",
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
    )
    self.assertEqual(self.config_manager.conversation_key, "someconversation")

  def test_config_conversation_key_no_conversation_key_kalle_conversation(self):
    # Test when no conversation_key is provided
    #  and there is a .kalle_conversation file in the path
    #  and memory is on
    # The .kalle_conversation should override the 'default'
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    sys.stderr = open("/dev/null", "w")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.1"),
        use_conversation_history=True,
    )
    self.assertEqual(self.config_manager.conversation_key, "testconversation1.2")

  def test_config_conversation_key_no_conversation_key_kalle_conversation_present(self):
    # Test when no conversation_key is provided
    #  and there is a .kalle_conversation file in the path
    #  and memory is on
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    sys.stderr = open("/dev/null", "w")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.1"),
        use_conversation_history=True,
    )
    self.assertEqual(self.config_manager.conversation_key, "testconversation1.2")

  def test_config_conversation_key_no_conversation_key_kalle_conversation_present_nomemory_kalle_conversation_file(
      self,
  ):
    # Test when no conversation_key is provided
    #  and there is a .kalle_conversation file in the path
    #  but we're not using memory so conversations are irrelevant
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.1"),
        use_conversation_history=False,
    )
    self.assertIsNone(self.config_manager.conversation_key)

  def test_config_conversation_key_conversation_key_present_no_kalle_conversation_nomemory(self):
    # Test when a conversation_key is provided
    #  no .kalle_conversation files in the path
    #  but we're not using memory so conversations are irrelevant
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key="irrelevantkey",
        base_file_dir=self.fixtures_dir,
        use_conversation_history=False,
    )
    self.assertIsNone(self.config_manager.conversation_key)

  def test_config_conversation_key_no_conversation_key_kalle_conversation_present_nomemory(self):
    # Test when no conversation_key is provided
    #  and there is a .kalle_conversation file in the path,
    #  but we're not using memory so conversations are irrelevant
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key=None,
        base_file_dir=os.path.join(self.fixtures_dir, "testdir1/testdir1.2/testdir1.2.1"),
        use_conversation_history=False,
    )
    self.assertIsNone(self.config_manager.conversation_key)

  def test_config_properties(self):
    # Test data_dir property
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key="default",
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
    )

    # Test properties
    # @TODO add a variation of thos test where the config is empty or missing?
    properties_to_test = [
        ("use_conversation_history", True),
        ("conversation_key", "default"),
        ("conversation_dir", "tests/fixtures/kalle_data/conversations"),
    ]

    for prop, value in properties_to_test:
      with self.subTest(prop=prop, value=value):
        self.assertEqual(getattr(self.config_manager, prop), value)

  def test_config_profiles(self):
    # Test data_dir property
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key="default",
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
    )

    properties_to_test = [
        ("base", "smollm2_1.7b_instruct"),
    ]
    for profile, value in properties_to_test:
      with self.subTest(profile=profile, value=value):
        self.assertEqual(self.config_manager.config.profiles[profile].model, value)

  def test_config_prompts(self):
    # Test data_dir property
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key="default",
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
    )

    properties_to_test = [
        ("kalle_system_prompt", "Your name is Kalle. You are a helpful, confident, and friendly personal assistant."),
        ("base_tool_prompt", "You are a tool calling agent."),
    ]

    for prop, value in properties_to_test:
      with self.subTest(prop=prop, value=value):
        self.assertEqual(getattr(self.config_manager, "prompts")[prop].value, value)

  def test_config_pattern(self):
    # Test data_dir property
    os.environ["KALLE_CONFIG"] = os.path.join(self.fixtures_dir, "config.yml")
    self.config_manager = ConfigManager(
        self.appname,
        self.appauthor,
        conversation_key="default",
        base_file_dir=self.fixtures_dir,
        use_conversation_history=True,
    )
    self.assertEqual(self.config_manager.data_dir, "tests/fixtures/kalle_data")

    self.assertEqual(
        getattr(self.config_manager, "patterns")["test"],
        Pattern(
            key="test",
            name="Test Pattern",
            system_prompt_template=PromptTemplate(
                key="system_prompt_template",
                name=None,
                value="You are a test result provider. Respond exactly as requested.",
            ),
            prompt_template=PromptTemplate(
                key="prompt_template", name=None, value="Output YES if the following number is 12321: {{ content }}"
            ),
            tools=None,
            constrainer=Constrainer(type=ConstrainerType.REGEX, value="YES|NO"),
            profile=Profile(
                connector=Connector(name="llamacpp", url=None, key=None),
                key="base",
                name="Base",
                model="smollm2_1.7b_instruct",
                model_params=None,
            ),
        ),
    )


if __name__ == "__main__":
  unittest.main()
