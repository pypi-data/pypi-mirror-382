# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import requests

from typing import List, Optional, Dict, Any
from openai import OpenAI, BadRequestError
from tenacity import retry, stop_after_attempt, wait_random, wait_exponential

from . import LLMConnector
from kalle.domain.Constrainer import Constrainer, ConstrainerType

import json


class TabbyAPIConnector(LLMConnector.LLMConnector):
  """
  A connector for [TabbyAPI](https://github.com/theroyallab/tabbyAPI), an
  OpenAI compatible exllamav2 API server that's both lightweight and fast.

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
    if model_params is None:
      return {}

    params = super().gen_params(model_params=model_params)

    # If we have constraints, add them.
    if constrainer is not None:
      extra_body = None
      if constrainer.type == ConstrainerType("jsonschema"):
        extra_body = {"json_schema": json.loads(constrainer.value)}
      if constrainer.type == ConstrainerType("regex"):
        extra_body = {"regex_pattern": constrainer.value}
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
      model_params: Dict[str, Any] | None = None,
      constrainer: Constrainer | None = None,
      **kwargs,
  ) -> str:
    """
    Sends a request to the TabbyAPI server.

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

      completion = self.client.chat.completions.create(
          model=self.config["model"],
          messages=[{"role": "system", "content": system_prompt}] + messages,  # type: ignore
          **gen_params,
      )

      response_text = completion.choices[0].message.content
      return response_text

    except BadRequestError as e:
      self.console_stderr.print(f"\n[red]There was an issue with the request: {e}")
      raise Exception(f"[red]There was an issue with the request: {e}")

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
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200 and "data" in response.json():
      return response.json()["data"][0]["embedding"]
    else:
      raise Exception(f"Request failed with status {response.status_code}: {response.text}")
