# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from typing import Dict, Any
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_random, wait_exponential

from . import LLMConnector


class GroqConnector(LLMConnector.LLMConnector):
  """
  A connector for interacting with the [Groq](https://groq.com/) API that
  leverages [](https://github.com/groq/groq-python)

  Attributes:
      config (dict): The configuration for the connector.
      client (Groq): The Groq client instance.
  """

  def __init__(self, config, /, **kwargs):
    """
    Initializes the GroqConnector instance.

    Args:
        config (dict): The configuration for the connector.
        **kwargs: Additional keyword arguments.
    """
    super().__init__(config, **kwargs)
    self.setup_client()

  def setup_client(self):
    """
    Sets up the Groq client instance using the provided configuration.
    """
    if self.config:
      self.client = Groq(
          api_key=self.config["api_key"],
      )

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
      model: str | None = None,
      **kwargs,
  ) -> str:
    """
    Sends a request to the Groq API.

    Args:
        system_prompt (str): The system prompt for the request.
        messages (list[dict]): The messages for the request.
        model (str | None): The model to use for the request. Defaults to None.
        model_params (Dict[str, Any] | None): The model parameters for the request. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        str | None: The response from the Groq API, or None if the request fails.
    """
    groq_messages = self.convert_messages_to_groq(messages)
    groq_messages.insert(0, {"role": "system", "content": system_prompt})

    params = self.gen_params(model_params)
    params["model"] = model or self.model or self.config["model"]
    params["messages"] = groq_messages
    params["max_tokens"] = params.get("max_tokens", 4096)

    response = self.client.chat.completions.create(**params)

    resp = response.choices[0].message.content

    return resp

  def convert_messages_to_groq(self, messages):
    """
    Converts a list of messages to the format expected by the Groq API.

    Args:
        messages (list[dict]): The messages to convert.

    Returns:
        list[dict]: The converted messages.
    """
    groq_messages = []

    for message in messages:
      if message["role"] == "system":
        continue

      groq_messages.append({"role": message["role"], "content": message["content"]})

    return groq_messages
