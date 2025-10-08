# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import sys

from typing import Any, Dict, List, Optional

from rich.console import Console

from kalle.lib.tokenizers.BaseTokenizer import BaseTokenizer
from kalle.lib.util.Tokenizers import Tokenizers
from kalle.domain.ModelConfig import ModelConfig


class LLMConnector:
  """
  A connector class for Large Language Models (LLMs).

  This class provides a basic structure for connecting to LLMs and making
  requests to models available via that connection. These could be direct via
  code, locally hosted or third party APIs.
  """

  def __init__(
      self,
      config,
      /,
      models_map: dict[str, ModelConfig],
      model: Optional[str] = None,
      console_stderr: Optional[Console] = None,
      debug: bool = False,
  ):
    """
    Initializes the LLMConnector object.

    Args:
        config (dict): The configuration dictionary for the connector.
        models_map (dict): A dictionary mapping model names to their configurations.
        model (str, optional): The name of the model to use. Defaults to None.
        console_stderr (Console, optional): A Console object for printing to stderr. Defaults to None.
        debug (bool, optional): A flag indicating whether to run in debug mode. Defaults to False.
    """
    self.config = config
    self.models_map = models_map
    self.model = model
    self.client = None
    self.llm_tokenizers = Tokenizers(self.config)
    self.tokenizer = None
    self.console_stderr = console_stderr or Console(file=sys.stderr)
    self.debug = debug
    self.setup_client()

  def get_model(self, _model_name=None) -> ModelConfig:
    """
    Gets the model configuration for the given model name.

    Args:
        _model_name (str, optional): The name of the model to get. Defaults to None.

    Returns:
        ModelConfig | None: The model configuration if found, otherwise None.
    """
    model_name = _model_name or self.model or self.config["model"]
    if model_name not in self.models_map:
      raise Exception(f"Model name key {model_name} is not in the models map for the current profile")

    return self.models_map[model_name]

  def get_tokenizer(self, _model_name=None) -> BaseTokenizer:
    """
    Gets the tokenizer for the given model name.

    Args:
        _model_name (str, optional): The name of the model to get. Defaults to None.

    Returns:
        BaseTokenizer | None: The tokenizer if found, otherwise None.
    """
    model_name = _model_name or self.config["model"]
    tokenizer_key = self.get_model(model_name).tokenizer
    tokenizer = self.llm_tokenizers.get_tokenizer(tokenizer_key, model_name)
    if tokenizer is None:
      raise Exception("Could not get tokenizer for {tokenizer_key} and {model_name}")

    return tokenizer

  def gen_params(self, model_params: Optional[Dict[str, Any]] = None) -> dict:
    """
    Generates a dictionary of parameters from the given model parameters.

    Args:
        model_params (ModelParams, optional): The list of model parameters. Defaults to None.

    Returns:
        dict: A dictionary of parameters.
    """
    params = {}

    model_map_params = self.get_model().params
    if model_map_params is not None:
      params = model_map_params

    if model_params is not None:
      for k, v in model_params.items():
        params[k] = v

    return params or {}

  def setup_client(self) -> None:
    """
    Sets up the client for the LLM.

    This method must be implemented by subclasses.
    """
    raise NotImplementedError("Subclasses must implement setup_client method")

  async def request(
      self,
      /,
      system_prompt: str,
      messages: list[dict],
      model_params: Optional[Dict[str, Any]] = None,
      **kwargs,
  ) -> str:
    """
    Makes a request to the LLM.

    This method must be implemented by subclasses.

    Args:
        system_prompt (str): The system prompt for the request.
        messages (list[dict]): The list of messages for the request.
        model_params (Dict[str, Any], optional): The list of model parameters. Defaults to None.
        constrainer (Constrainer, optional): The constrainer for the request. Defaults to None.

    Returns:
        str | None: The response from the LLM if successful, otherwise None.
    """
    raise NotImplementedError("Subclasses must implement request method")

  async def complete(
      self,
      /,
      prompt: str,
      model_params: Optional[Dict[str, Any]] = None,
      **kwargs,
  ) -> str:
    """
    Makes a request to the LLM.

    This method must be implemented by subclasses.

    Args:
        system_prompt (str): The system prompt for the request.
        messages (list[dict]): The list of messages for the request.
        model_params (Dict[str, Any], optional): The list of model parameters. Defaults to None.
        constrainer (Constrainer, optional): The constrainer for the request. Defaults to None.

    Returns:
        str | None: The response from the LLM if successful, otherwise None.
    """
    raise NotImplementedError("Subclasses must implement request method")

  async def embed(
      self,
      text: str,
      /,
      model: Optional[str] = None,
      **kwargs,
  ) -> Optional[List]:
    """
    Makes a request to fetch embeddings for the provided text.

    This method must be implemented by subclasses.

    Args:
        model (str): The model to use to generate the emebdding.
        text (str): The text to generate an embedding for.

    Returns:
        str | None: The embedding json if successful, otherwise None.
    """
    raise NotImplementedError("Subclasses must implement request method")

  async def rerank(
      self,
      query: str,
      items: List[str],
      /,
      **kwargs,
  ) -> Optional[List[Dict]]:
    """
    Makes a request to re-rank a set of text strings based on the query.

    This method must be implemented by subclasses.

    Args:
        query (str): The query for ranking.
        items (List[str]): The list of test strings to be ranked.

    Returns:
        str | None: The embedding json if successful, otherwise None.
    """
    raise NotImplementedError("Subclasses must implement request method")
