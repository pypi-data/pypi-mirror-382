# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import json
import contextlib
import sys

from typing import Any, Dict
from llama_cpp import Llama

from kalle.domain.Constrainer import Constrainer, ConstrainerType
from . import LLMConnector


class LlamaCppConnector(LLMConnector.LLMConnector):
  """
  A connector that uses Llama.cpp to run language models locally. It uses the
  [python bindings for llama.cpp](https://github.com/abetlen/llama-cpp-python).

  It allows for setting up a client, generating parameters, and making requests.
  """

  def __init__(self, config, /, **kwargs):
    """
    Initializes the LlamaCppConnector.

    Args:
        config: The configuration for the connector.
        **kwargs: Additional keyword arguments that may be needed by the parent.
    """
    super().__init__(config, **kwargs)
    self.setup_client()

  def setup_client(self):
    """
    Sets up the client.

    This method creates a new client based on the provided configuration.
    It sets up the model path, verbose mode, and other parameters.
    """
    if self.config:
      model_config = self.get_model(self.config["model"])
      model_path = os.path.join(self.config["models_dir"], str(model_config.path))

      params: dict[str, Any] = {
          "verbose": False,
          # n_gpu_layers=-1, # Uncomment to use GPU acceleration
          # seed=1337, # Uncomment to set a specific seed
      }
      if model_config.context_size is not None:
        params["n_ctx"] = model_config.context_size

      if model_config.path is not None:

        if not os.path.exists(model_path):
          self.console_stderr.print(f"[red]The local model path {model_path} doesn't exist.")
          raise Exception(f"The local model path {model_path} doesn't exist.")

        with contextlib.redirect_stderr(open(os.devnull, "w")):
          self.client = Llama(model_path=model_path, **params)
      else:
        with contextlib.redirect_stderr(open(os.devnull, "w")):
          self.client = Llama.from_pretrained(
              repo_id=model_config.repo_id or "",
              filename=model_config.filename,
              **params,
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
    Makes a request to the LLaMA C++ model.

    Args:
        system_prompt: The system prompt for the request.
        messages: The messages for the request.
        model: The model to use for the request.
        model_params: The model parameters for the request.
        constrainer: The constrainer for the request.
        **kwargs: Additional keyword arguments.

    Returns:
        The response from the model.
    """
    params = self.gen_params(model_params)
    if constrainer is not None and constrainer.type == ConstrainerType("jsonschema"):
      params["response_format"] = {
          "type": "json_object",
          "schema": json.loads(constrainer.value),
      }

    output = self.client.create_chat_completion(
        messages=messages,  # type: ignore
        **params,
    )

    return output.get("choices")[0].get("message").get("content")  # type: ignore
