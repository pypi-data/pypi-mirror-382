# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import sys
import json

from typing import Dict, Any
from openai import OpenAI, BadRequestError, AuthenticationError
from tenacity import retry, stop_after_attempt, wait_random, wait_exponential

from kalle.domain.Constrainer import Constrainer, ConstrainerType
from . import LLMConnector


class OpenAIConnector(LLMConnector.LLMConnector):

  def __init__(self, config, /, **kwargs):
    super().__init__(config, **kwargs)
    self.setup_client()

  def setup_client(self):
    if self.config:
      self.client = OpenAI(
          base_url=self.config["url"],
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
      constrainer: Constrainer | None = None,
      **kwargs,
  ) -> str:
    try:
      params = self.gen_params(model_params)

      if constrainer is not None and constrainer.type == ConstrainerType("jsonschema"):
        params["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "schema",  # this isn't relevant to our use
                "strict": True,
                "schema": json.loads(constrainer.value),
            },
        }

      completion = self.client.chat.completions.create(
          model=self.model or self.config["model"],
          messages=[{"role": "system", "content": system_prompt}] + messages,  # type: ignore
          **params,
      )

      response_text = completion.choices[0].message.content
      return response_text

    except AuthenticationError as e:
      errstr = e.body or "UNKNOWN AUTH ERROR"
      if isinstance(e.body, dict):
        errstr = e.body.get("message", "UNKNOWN AUTH ERROR")
      self.console_stderr.print(
          f"\n[red][bold]There was an issue authenticating with OpenAI's API:[/bold] {str(errstr)}"
      )
      raise Exception(f"\nThere was an issue authenticating with OpenAI's API: {str(errstr)}")

    except BadRequestError as e:
      self.console_stderr.print(f"\n[red][bold]There was an issue with the request:[/bold] {e}")
      sys.exit(65)
