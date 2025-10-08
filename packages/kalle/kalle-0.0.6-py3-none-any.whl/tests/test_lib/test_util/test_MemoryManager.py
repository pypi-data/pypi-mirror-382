# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import unittest

from tempfile import TemporaryDirectory

from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.util.ProfileManager import ProfileManager
from kalle.lib.util.MemoryManager import MemoryManager


class TestMemoryManager(unittest.IsolatedAsyncioTestCase):

  def setUp(self):
    appname = "kalle"
    appauthor = "fe2"
    self.fixtures_dir = os.path.join(os.path.dirname(__file__), "../../fixtures")
    self.config_file = os.path.join(self.fixtures_dir, "config.yml")
    os.environ["KALLE_CONFIG"] = self.config_file
    self.temp_dir = TemporaryDirectory()
    os.environ["KALLE_DATA_DIR"] = self.temp_dir.name
    self.config_manager = ConfigManager(
        appname, appauthor, base_file_dir=self.fixtures_dir, use_conversation_history=False
    )
    self.maxDiff = None

    self.embedding_profile = ProfileManager(self.config_manager, "embed")
    self.reranking_profile = ProfileManager(self.config_manager, "rerank")
    self.relevance_profile = ProfileManager(self.config_manager, "base")
    self.enrichment_profile = ProfileManager(self.config_manager, "base")

    os.makedirs(self.config_manager.data_dir, exist_ok=True)
    self.memory_manager = MemoryManager(
        {
            "data_dir": self.config_manager.data_dir,
            "memory": self.config_manager.config.memory,
        },
        embedding_connector=self.embedding_profile.connector,
        enrichment_connector=self.enrichment_profile.connector,
        reranking_connector=self.reranking_profile.connector,
        relevance_connector=self.relevance_profile.connector,
        db_name="test",
    )

  def tearDown(self):
    self.temp_dir.cleanup()

  async def test_init(self):
    self.assertIsNotNone(self.memory_manager)

  # @unittest.skip("Needs extern enrichment model")
  async def test_enrich(self):
    result = await self.memory_manager.enrich("My favorite color is red")
    self.assertIn("QUESTIONS:\n1. What is your favorite color?", str(result))

  @unittest.skip("Needs extern embedding model")
  async def test_store(self):
    result = await self.memory_manager.store("text", enrich=True)
    self.assertEqual(result, "Embedding stored in database")

  @unittest.skip("Needs extern embedding model")
  async def test_query(self):
    result = await self.memory_manager.query("query")
    self.assertIsInstance(result, list)

  @unittest.skip("Needs extern embedding model")
  async def test_embed(self):
    result = await self.memory_manager.embed("This is a test")
    self.assertEqual(type(result), list)

  @unittest.skip("Needs extern rerank model")
  async def test_rerank(self):
    result = await self.memory_manager.rerank("query", ["item1", "item2"])
    self.assertEqual(result, [{"relevance_score": 0.5, "index": 0}])

  @unittest.skip("Needs extern rerank model")
  async def test_relevance(self):
    result = await self.memory_manager.relevance("prompt", "text")
    self.assertEqual(result, "YES")


if __name__ == "__main__":
  unittest.main()
