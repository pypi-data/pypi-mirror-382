# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import sys
import os
import requests

from typing import Any, Dict, List, Optional
from openai import OpenAI, BadRequestError
from tenacity import retry, stop_after_attempt, wait_random, wait_exponential

from . import LLMConnector
from kalle.domain.Constrainer import Constrainer, ConstrainerType

import json


class VllmAPIConnector(LLMConnector.LLMConnector):
  """
  A connector for [vllm](https://github.com/vllm-project/vllm), "A high-throughput
  and memory-efficient inference and serving engine for LLMs"

  It uses the [OpenAI python library[(https://github.com/openai/openai-python).

  Attributes:
      config (dict): The configuration for the connector.
  """

  def __init__(self, config, /, **kwargs):
    """
    Initializes the connector interface.

    Args:
        config (dict): The configuration for the connector.
        **kwargs: Additional keyword arguments.
    """
    super().__init__(config, **kwargs)

  def setup_client(self):
    """
    Sets up the OpenAI client with the provided configuration.
    """
    self.client = OpenAI(
        base_url=self.config["url"],
        api_key=self.config["api_key"],
        timeout=60 * 60 * 60,
    )

  def gen_params(
      self, model_params: Optional[Dict[str, Any]] = None, constrainer: Optional[Constrainer] = None
  ) -> dict:
    """
    Generates the model parameters for the API request.

    Args:
        model_params (Dict[str, Any] | None): The model parameters.
        constrainer (Constrainer | None): The constrainer.

    Returns:
        dict: The generated parameters.
    """
    params = super().gen_params(model_params=model_params)

    extra_body = None

    if "extra_body" in params:
      extra_body = params["extra_body"]

    # If we have constraints, add them.
    if constrainer is not None:
      extra_body = extra_body or {}

      if constrainer.type == ConstrainerType("jsonschema"):
        extra_body["guided_json"] = json.loads(constrainer.value)
      if constrainer.type == ConstrainerType("regex"):
        extra_body["guided_regex"] = constrainer.value
      if constrainer.type == ConstrainerType("gbnf"):
        extra_body["grammar"] = constrainer.value

    if extra_body is not None:
      params["extra_body"] = extra_body

    return params

  @retry(
      reraise=True,
      wait=wait_exponential(multiplier=1, min=0.2, max=3) + wait_random(0, 0.3),
      stop=stop_after_attempt(3),
  )
  async def request(
      self,
      /,
      system_prompt: str,
      messages: list[dict],
      model_params: Optional[Dict[str, Any]] = None,
      constrainer: Optional[Constrainer] = None,
      **kwargs,
  ) -> str:
    """
    Sends a request to the vllm API server.

    Args:
        system_prompt (str): The system prompt.
        messages (list[dict]): The messages.
        model_params (Dict[str, Any] | None): The model parameters.
        constrainer (Constrainer | None): The constrainer.

    Returns:
        str | None: The response text or None if the request fails.
    """
    try:
      gen_params = self.gen_params(model_params=model_params, constrainer=constrainer)

      if self.config.get("debug", False):
        self.console_stderr.print(f"[magenta]Model Params: {gen_params}")

      completion = self.client.chat.completions.create(
          model=self.config["model"],
          messages=[{"role": "system", "content": system_prompt}] + messages,  # type: ignore
          **gen_params,
      )

      response_text = completion.choices[0].message.content

      if self.config.get("debug", False):
        self.console_stderr.print(f"[magenta]RAW Response: {response_text}")

      if "</think>" in response_text and "<think>" not in response_text:
        response_text = f"<think>{response_text}"

      return response_text

    except BadRequestError as e:
      self.console_stderr.print(f"\n[red]There was an issue with the request: {e}")
      raise Exception(f"\n[red]There was an issue with the request: {e}")

  @retry(
      reraise=True,
      wait=wait_exponential(multiplier=1, min=0.2, max=3) + wait_random(0, 0.3),
      stop=stop_after_attempt(3),
  )
  async def complete(
      self,
      /,
      prompt: str,
      model_params: Optional[Dict[str, Any]] = None,
      constrainer: Optional[Constrainer] = None,
      **kwargs,
  ) -> str:
    """
    Sends a request to the vllm API server.

    Args:
        prompt: (str): The prompt.
        model_params (Dict[str, Any] | None): The model parameters.
        constrainer (Constrainer | None): The constrainer.

    Returns:
        str | None: The response text or None if the request fails.
    """

    try:
      gen_params = self.gen_params(model_params=model_params, constrainer=constrainer)

      if self.config["debug"]:
        self.console_stderr.print(f"[magenta]Model Params: {gen_params}")

      completion = self.client.completions.create(
          model=self.config["model"],
          prompt=[prompt],
          **gen_params,
      )

      response_text = completion.choices[0].text
      if "</think>" in response_text and "<think>" not in response_text:
        response_text = f"<think>{response_text}"

      return response_text

    except BadRequestError as e:
      self.console_stderr.print(f"\n[red]There was an issue with the request: {e}")
      raise e

  @retry(
      reraise=True,
      wait=wait_exponential(multiplier=1, min=0.2, max=3) + wait_random(0, 0.3),
      stop=stop_after_attempt(3),
  )
  async def embed(
      self,
      text: str,
      /,
      model: Optional[str] = None,
      **kwargs,
  ) -> List[float]:
    """
    Sends text to the vllm API server to fetch an embedding.

    Args:
        text (str): The text to embed.

    Returns:
        str: The response text or None if the request fails.
    """

    url = os.path.join(self.config["url"], "embeddings")
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model or self.config["model"],
        "input": [text],
        # "encoding_format": "float",
        # "add_special_tokens": True,
        # "user": "string",
        # "additional_data": "string",
        # "dimensions": 1563,
        # "truncate_prompt_tokens": 1,
        # "priority": 0,
        # "additionalProp1": {}
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200 and "data" in response.json():
      return response.json()["data"][0]["embedding"]
    else:
      raise Exception(f"Request failed with status {response.status_code}: {response.text}")

  @retry(
      reraise=True,
      wait=wait_exponential(multiplier=1, min=0.2, max=3) + wait_random(0, 0.3),
      stop=stop_after_attempt(3),
  )
  async def rerank(
      self,
      query: str,
      items: List[str],
      /,
      model: Optional[str] = None,
      **kwargs,
  ) -> Optional[List[Dict]]:
    """
    Sends text to the vllm API server to fetch an embedding.

    Args:
        text (str): The text to embed.

    Returns:
        str: The response text or None if the request fails.
    """

    if len(items) < 2:
      return None

    url = os.path.join(self.config["url"], "rerank")
    headers = {"Content-Type": "application/json"}

    data = {
        "model": model or self.config["model"],
        "query": query,
        "documents": items,
        # "top_n": 0,
        # "truncate_prompt_tokens": 1,
        # "additional_data": "string",
        # "priority": 0,
        # "additionalProp1": {}
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200 and "results" in response.json():
      return response.json()["results"]
    else:
      raise Exception(f"Request failed with status {response.status_code}: {response.text}")
