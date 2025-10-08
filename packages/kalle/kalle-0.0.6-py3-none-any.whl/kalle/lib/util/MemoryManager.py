# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import re
import sys
import sqlite3
import sqlite_vec
# import numpy as np
# import subprocess
# import json
import struct
from typing import Any, Dict, List, Optional

from rich.console import Console

from kalle.lib.connectors.LLMConnector import LLMConnector
from kalle.domain.Constrainer import Constrainer, ConstrainerType


class MemoryManager:

  def __init__(
      self,
      config: Dict[str, Any],
      /,
      embedding_connector: LLMConnector,
      reranking_connector: LLMConnector,
      enrichment_connector: LLMConnector,
      relevance_connector: LLMConnector,
      db_name: Optional[str] = None,
      console_stderr: Optional[Console] = None,
      debug: bool = False,
  ):
    self.config = config

    if self.config.get("memory", None) is None:
      raise Exception("Memory configuration is not found, please set that up first")
    self.embedding_connector = embedding_connector
    self.reranking_connector = reranking_connector
    self.enrichment_connector = enrichment_connector
    self.relevance_connector = relevance_connector
    self.console_stderr = console_stderr or Console(file=sys.stderr)
    self.debug = debug

    db_name = db_name or self.config["memory"].knowledgebase or "knowledge"
    db_path = os.path.join(config["data_dir"], f"{db_name}.db")

    self.db = sqlite3.connect(db_path)
    self.db.enable_load_extension(True)
    sqlite_vec.load(self.db)
    self.db.enable_load_extension(False)
    self._create_tables()

  def _create_tables(self):
    embedding_dimensions = int(self.config["memory"].embedding_dimensions or 1024)
    self.db.execute("CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, text TEXT, ref TEXT);")
    self.db.execute(
        f"CREATE VIRTUAL TABLE IF NOT EXISTS vec_items USING vec0(embedding float[{embedding_dimensions}]);"
    )
    self.db.commit()

  @staticmethod
  def serialize_f32(vector: List[float]) -> bytes:
    return struct.pack(f"{len(vector)}f", *vector)

  async def enrich(self, text: str) -> Optional[str]:
    result = await self.enrichment_connector.request(
        system_prompt="You are a data enricher, follow the instructions exactly",
        messages=[
            {
                "role": "user",
                "content": f"Come up with an un-numbered list of the top 10 most likely questions that can be answered by this text: {text}. Only output the questions.",
            }
        ],
    )

    if result is None:
      raise Exception("Data enrichment failed")

    return f"QUESTIONS:\n{result}"

  async def embed(self, text: str) -> Optional[list[float]]:
    result = await self.embedding_connector.embed(text)
    if not result:
      return None

    if isinstance(result, list):
      return result

  async def rerank(self, query: str, items: List[str]) -> Optional[List[Dict]]:
    result = await self.reranking_connector.rerank(query, items)
    if not result:
      return None

    if isinstance(result, list):
      return result

  async def relevance(self, prompt: str, text: str) -> Optional[str]:
    result = await self.relevance_connector.request(
        system_prompt="You check whether a section of content is relevant to a given prompt, follow the instructions exactly",
        constrainer=Constrainer(type=ConstrainerType.REGEX, value="YES|NO"),
        messages=[
            {
                "role": "user",
                "content": f"Provide a YES or NO answer to whether the content is relevant to the prompt: {prompt}\n\nHere is the content:\n {text}",
            }
        ],
    )

    if result is None:
      raise Exception("Data relevanct check failed")

    return result

  async def reword(self, prompt: str) -> Optional[str]:
    result = await self.relevance_connector.request(
        system_prompt="You are RAG prompt enhancer that will re-word prompts to work better for vectordb cosine similarity queries, follow the instructions exactly and respond only with what is requested.",
        temperature=0.00000001,
        constrainer=Constrainer(type=ConstrainerType.REGEX, value="^The reworded prompt is: [A-Z].*"),
        messages=[
            {
                "role": "user",
                "content": f"Reword the following prompt: {prompt}",
            }
        ],
    )

    if result is None:
      raise Exception("Prompt rewording failed")

    return result[24:]

  # @TODO eventually make enrich a callback so that different enrichment methods could be used?
  async def store(self, text: str, ref: Optional[str] = None, enrich: Optional[bool] = False) -> str:
    embed_text = text
    if enrich:
      enrich_text = await self.enrich(text)
      embed_text = f"{text}\n\n{enrich_text}"
    embedding = await self.embed(embed_text)
    if embedding is None:
      return "Failed to generate embedding"
    embedding_list = embedding

    with self.db:
      cursor = self.db.cursor()
      cursor.execute("SELECT MAX(rowid) FROM items")
      max_rowid = cursor.fetchone()[0]
      rowid = max_rowid + 1 if max_rowid is not None else 1

      cursor.execute("INSERT INTO items(id, ref, text) VALUES(?, ?, ?)", (rowid, ref, text))

      cursor.execute(
          "INSERT INTO vec_items(rowid, embedding) VALUES (?, ?)", (rowid, self.serialize_f32(embedding_list))
      )

    return "Embedding stored in database"

  async def query(self, text: str, /, limit: Optional[int] = None) -> List[dict]:
    # SmolLM2 isn't working well, revisit at some point and probably fine-tune a model to make this work
    # text = await self.reword(text)
    # print(f"REWORDED: -{text}-")

    if limit is None:
      limit = self.config.memory.max_knowledgebase_results or 30

    print(f"QUERY LIMIT: {limit}")
    print(f"QUERY TEXT: {text}")

    embedding = await self.embed(text)
    if embedding is None:
      raise Exception("Could not embed prompt for memory retrieval")
    query_embedding = embedding

    rows = self.db.execute(
        """
            SELECT rowid, vec_distance_cosine(embedding, ?) AS distance
            FROM vec_items
            ORDER BY distance
            LIMIT ?
            """,
        (self.serialize_f32(query_embedding), limit),
    ).fetchall()

    results = []
    for row in rows:
      row_id = row[0]
      distance = row[1]
      text_row = self.db.execute("SELECT ref, text FROM items WHERE id = ?", (row_id,)).fetchone()

      # ignore results that are empty
      if text_row is not None and len(text_row[1]) > 0:
        results.append(
            {
                "id": row_id,
                "distance": distance,
                "ref": text_row[0],
                "text": text_row[1],
            }
        )

    rerank_items = [r["text"] for r in results]
    rerank_results = await self.rerank(text, rerank_items)

    ranked_results = []
    if isinstance(rerank_results, list):
      for rerank_result in rerank_results:
        # probably redo this with a weighted combined score
        if "relevance_score" in rerank_result:
          # Let's eliminate things that are very non-relevant as scored by the reranker
          # print("-_-"*20)
          # print(f'{rerank_result["relevance_score"]} < {self.config["memory"]["min_relevance_cutoff"]}')
          # print(f'{rerank_result["relevance_score"]} < {self.config["memory"]["min_relevance_cutoff"] * 5}')
          # print(f'LRR: -{len(ranked_results)}-')
          # print(f'{results[rerank_result["index"]]["text"]}')
          if len(ranked_results) >= 3:
            if rerank_result["relevance_score"] < self.config["memory"]["min_relevance_cutoff"]:
              continue

            # do the costly check for relevance
            relevance_check_result = await self.relevance(text, results[rerank_result["index"]]["text"])

            print(relevance_check_result)
            if relevance_check_result != "YES":
              continue

          results[rerank_result["index"]]["relevance_score"] = rerank_result["relevance_score"]
          ranked_results.append(results[rerank_result["index"]])

    return ranked_results
