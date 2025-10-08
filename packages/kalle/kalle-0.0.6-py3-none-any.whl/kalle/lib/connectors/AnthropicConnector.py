# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from typing import Any, Dict
import anthropic

from tenacity import retry, stop_after_attempt, wait_random, wait_exponential

from . import LLMConnector


class AnthropicConnector(LLMConnector.LLMConnector):
  """
  A connector for interacting with the Anthropic API using this library:
  [](https://github.com/anthropics/anthropic-sdk-python)

  This class provides a interface for sending requests to the Anthropic API
  and handling the responses.

  An Anthrropic API account is required. Details can be found here to set one
  up: [](https://docs.anthropic.com/en/docs/initial-setup)
  """

  def __init__(self, config, /, **kwargs):
    """
    Initializes the AnthropicConnector instance.

    Args:
        config (dict): The configuration for the connector.
        **kwargs: Additional keyword arguments.
    """
    super().__init__(config, **kwargs)

    self.setup_client()

  def setup_client(self):
    """
    Sets up the Anthropic client using the provided configuration. An API
    key is required.
    """
    if self.config:
      self.client = anthropic.Anthropic(
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
    Sends a request to the Anthropic API.

    Args:
        system_prompt (str): The system prompt for the request.
        messages (list[dict]): The messages for the request.
        model (str | None): The model to use for the request. Defaults to None.
        model_params (Dict[str, Any] | None): The model parameters for the request. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        str | None: The response from the Anthropic API, or None if the request fails.
    """
    anthropic_messages = self.convert_messages_to_anthropic(messages)

    params = self.gen_params(model_params)
    params["system"] = system_prompt
    # required by Anthropic
    params["model"] = model or self.model or self.config["model"]
    params["max_tokens"] = params.get("max_tokens", 8192)
    params["messages"] = anthropic_messages

    client = anthropic.Anthropic()

    think = ""
    resp = ""
    text_stream = ""

    with self.client.messages.stream(**params) as stream:
      for text in stream.text_stream:
        text_stream += text
        if self.debug:
          self.console_stderr.print(f"[bright_black]stream.text_stream: {text}")

      for event in stream:
        if event.type == "content_block_delta":
          if event.delta.type == "thinking_delta":
            think += event.delta.thinking

            if self.debug:
              self.console_stderr.print(f"[bright_black]event.delta.thinking: {event.delta.thinking}")
          elif event.delta.type == "text_delta":
            resp += event.delta.text

            if self.debug:
              self.console_stderr.print(f"[bright_black]event.delta.text: {event.delta.text}")

    # think = None
    # resp = None
    # for r in response.content:
    #  if r.type == "thinking" and think is None:
    #    think = r.thinking
    #  if r.type == "text" and resp is None:
    #    resp = r.text

    if resp == "" and text_stream != "":
      resp = text_stream

    # re-integrate the thinking response as we separate it ourselves later
    if think != "":
      resp = f"<think>{think}</think>\n{resp}"

    if resp == "":
      raise Exception("Could not retrive response from Anthropic API response")

    return resp

  def convert_messages_to_anthropic(self, messages):
    """
    Converts the provided messages to the format expected by the Anthropic API.

    Args:
        messages (list[dict]): The messages to convert.

    Returns:
        list[dict]: The converted messages.
    """
    anthropic_messages = []

    for message in messages:
      if message["role"] == "system":
        continue

      role = message["role"]
      content = message["content"]
      anthropic_message = {"role": role, "content": [{"type": "text", "text": content}]}
      anthropic_messages.append(anthropic_message)

    return anthropic_messages
