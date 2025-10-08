# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import asyncio
import json
from typing import Any, Dict

import aiohttp

from rich.panel import Panel
from rich.syntax import Syntax
from tenacity import retry, stop_after_attempt, wait_random, wait_exponential


from kalle.domain.Constrainer import Constrainer, ConstrainerType
from . import LLMConnector


class OllamaConnector(LLMConnector.LLMConnector):
  """
  A connector for interacting with the [Ollama](https://ollama.com/) API.

  Attributes:
      config (dict): The configuration for the connector.
  """

  def __init__(self, config, /, **kwargs):
    """
    Initializes the OllamaConnector.

    Args:
        config (dict): The configuration for the connector.
        **kwargs: Additional keyword arguments.
    """
    super().__init__(config, **kwargs)
    self.setup_client()

  def setup_client(self):
    """
    Sets up the client for the Ollama API.

    This method is currently a no-op, but can be overridden in the future to perform any necessary setup.
    """
    pass

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
    Sends a request to the Ollama API.

    Args:
        system_prompt (str): The system prompt to send with the request.
        messages (list[dict]): The messages to send with the request.
        model_params (Dict[str, Any] | None, optional): The model parameters to use. Defaults to None.
        constrainer (Constrainer | None, optional): The constrainer to use. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        str | None: The response from the Ollama API, or None if the request fails.
    """
    headers = {"Content-Type": "application/json"}

    params = {}
    params["options"] = self.gen_params(self.get_model().params)
    params["model"] = self.model or self.config["model"]
    params["system"] = system_prompt
    params["stream"] = False

    # This requires ollama > 0.5
    if constrainer is not None and constrainer.type == ConstrainerType("jsonschema"):
      params["format"] = json.loads(constrainer.value)

    if params["model"] is None:
      self.console_stderr.print("[red]Need to specify a model")
      raise Exception("Need to specify a model")

    if self.debug:
      self.console_stderr.print(
          Panel(
              Syntax(json.dumps(params, indent=4), "json", word_wrap=True),
              title="[bold magenta]Model Parameters",
              style="magenta",
          )
      )
    params["messages"] = [{"role": "system", "content": system_prompt}] + messages  # type: ignore

    async with aiohttp.ClientSession() as session:
      while True:
        await asyncio.sleep(1)
        async with session.post(self.config["url"], headers=headers, data=json.dumps(params)) as response:
          resp = await response.json()

          if "error" in resp:
            self.console_stderr.print(
                f"[red][bold]There was an error getting a response from Ollama:[/bold] {resp['error']}"
            )
            raise Exception(f"There was an error getting a response from Ollama: {resp['error']}")

          if "message" not in resp:
            self.console_stderr.print("[red]There was an error getting a response from Ollama")
            if self.debug:
              self.console_stderr.print(f"[red]{resp}")

            raise Exception(f"{resp}")

          return resp["message"]["content"]
