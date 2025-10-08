# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import unittest

from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.connectors.LLMConnector import LLMConnector

from kalle.lib.connectors.AnthropicConnector import AnthropicConnector
from kalle.lib.connectors.GoogleVertexAIConnector import GoogleVertexAIConnector
from kalle.lib.connectors.GroqConnector import GroqConnector
from kalle.lib.connectors.LlamaCppConnector import LlamaCppConnector
from kalle.lib.connectors.OllamaConnector import OllamaConnector
from kalle.lib.connectors.OpenAIConnector import OpenAIConnector
from kalle.lib.connectors.TabbyAPIConnector import TabbyAPIConnector
from kalle.lib.connectors.VllmAPIConnector import VllmAPIConnector

from kalle.lib.util.LLMConnectors import LLMConnectors
from kalle.domain.Profile import Profile
from kalle.domain.Connector import Connector, connector_factory


class TestLLMConnectors(unittest.TestCase):

  def setUp(self):
    appname = "kalle"
    appauthor = "fe2"
    self.fixtures_dir = os.path.join(os.path.dirname(__file__), "../../fixtures")
    self.config_file = os.path.join(self.fixtures_dir, "config.yml")
    os.environ["KALLE_CONFIG"] = self.config_file
    self.config = ConfigManager(
        appname, appauthor, conversation_key="default", base_file_dir=self.fixtures_dir, use_conversation_history=False
    )
    self.llm_connectors = LLMConnectors(self.config)

  def test_init(self):
    self.assertEqual(self.llm_connectors.config_manager, self.config)
    self.assertEqual(len(self.llm_connectors.connectors), 0)

  def test_get_connector_base(self):
    connector = self.llm_connectors.get_connector(
        Profile(key="base", connector=Connector(name="llamacpp")), "smollm2_1.7b_instruct"
    )
    self.assertIsInstance(connector, LLMConnector)
    # only check this once
    self.assertEqual(len(self.llm_connectors.connectors), 1)

  def test_get_connectors(self):
    properties_to_test = [
        ("anthropic", AnthropicConnector),
        ("groq", GroqConnector),
        ("ollama", OllamaConnector),
        ("openai", OpenAIConnector),
        ("tabbyapi", TabbyAPIConnector),
        ("vllmapi", VllmAPIConnector),
    ]

    for name, connector_class in properties_to_test:
      with self.subTest(name=name, connector_class=connector_class):
        connector = self.llm_connectors.get_connector(
            Profile(key=name, connector=connector_factory(data={"name": name})), None
        )
        self.assertIsInstance(connector, connector_class)

  def test_get_connector_llamacpp(self):
    connector = self.llm_connectors.get_connector(
        Profile(key="llamacpp", connector=connector_factory(data={"name": "llamacpp"})), "smollm2_1.7b_instruct"
    )
    self.assertIsInstance(connector, LlamaCppConnector)

  def test_get_connector_vertexai(self):
    # we can't fully instantiate the connector with just test data so we get to a known failure
    with self.assertRaises(ValueError):
      connector = self.llm_connectors.get_connector(
          Profile(
              key="vertexai",
              connector=connector_factory(
                  data={"name": "vertexai", "project_id": "1", "credentials_path": "tests/fixtures/fake_creds.json"}
              ),
          ),
          None,
      )
      self.assertIsInstance(connector, GoogleVertexAIConnector)

  def test_get_connector_missing(self):
    # we can't fully instantiate the connector with just test data so we get to a known failure
    with self.assertRaises(ValueError):
      connector = self.llm_connectors.get_connector(
          Profile(key="llamacpp", connector=connector_factory(data={"name": "missing"})), "smollm2_1.7b_instruct"
      )
      self.assertIsInstance(connector, LLMConnector)

  def test_get_connector_cached(self):
    connector = self.llm_connectors.get_connector(
        Profile(key="base", connector=connector_factory(data={"name": "llamacpp"})), "smollm2_1.7b_instruct"
    )
    self.assertIsInstance(connector, LLMConnector)

    connector2 = self.llm_connectors.get_connector(
        Profile(key="base", connector=connector_factory(data={"name": "llamacpp"})), "smollm2_1.7b_instruct"
    )
    self.assertEqual(connector, connector2)


if __name__ == "__main__":
  unittest.main()
