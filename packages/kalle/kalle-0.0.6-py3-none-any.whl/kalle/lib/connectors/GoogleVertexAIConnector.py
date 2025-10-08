# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import sys
from typing import Any, Dict
import httpx

from rich.panel import Panel
from rich.syntax import Syntax
from tenacity import retry, stop_after_attempt, wait_random, wait_exponential

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

from . import LLMConnector


"""
Module for connecting to Google Vertex AI.

This module provides a class for connecting to Google Vertex AI and performing
various operations such as authentication, building endpoint URLs, and making
requests to the Vertex AI API.

The following library is used:
[](https://pypi.org/project/vertexai/)

To access Google APIs, kalle will need credentials. These can be created based
on these instructions [OAuth client ID credentials](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id)

The path to the downloaded credentials must be specified in the config file via
the `google_app_credentials_path` parameter.i

The project needs to have the Vertex AI API enabled and the relevant models
have to be enabled within Vertex AI in the console.

[](https://cloud.google.com/vertex-ai)

"""


creds = None
SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


class GoogleVertexAIConnector(LLMConnector.LLMConnector):
  """
  A class for connecting to Google Vertex AI.

  This class provides methods for authenticating with Google Vertex AI,
  building endpoint URLs, and making requests to the Vertex AI API.

  Attributes:
      project_id (str): The ID of the Google Cloud project.
      region (str): The region of the Google Cloud project.
  """

  def __init__(self, config, /, **kwargs):
    """
    Initializes the GoogleVertexAIConnector instance.

    Args:
        config (dict): A dictionary containing the configuration for the
            connector.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    super().__init__(config, **kwargs)

    # Retrieve Google Cloud Project ID and Region from environment variables
    self.project_id = self.config["project_id"] or os.environ.get("GOOGLE_PROJECT_ID")
    self.region = self.config["region"] or os.environ.get("GOOGLE_REGION")
    self.credentials_path = self.config["credentials_path"] or os.environ.get("GOOGLE_APP_CREDENTIALS_PATH")

    try:
      self.auth()
    except FileNotFoundError as e:
      self.console_stderr.print(f"[red][bold]Google VertexAI Auth Error: File not found:[/bold] {e.filename}")
      raise Exception(f"[red][bold]Google VertexAI Auth Error: File not found:[/bold] {e.filename}")

  def auth(self):
    """
    Authenticates with Google Vertex AI.

    This method checks if credentials are already available, and if not,
    it prompts the user to log in and obtain credentials.

    Returns:
        None
    """
    global creds
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = os.path.join(self.config["token_cache_dir"], "vertexai_connector_token.json")

    if os.path.exists(token_path):
      creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
      else:
        flow = InstalledAppFlow.from_client_secrets_file(self.config["credentials_path"], SCOPES)
        creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open(token_path, "w") as token:
        token.write(creds.to_json())

  def build_endpoint_url(
      self,
      region: str,
      project_id: str,
      model_name: str,
      publisher: str = "google",
      streaming: bool = False,
  ):
    """
    Builds the endpoint URL for the Vertex AI API.

    Args:
        region (str): The region of the Google Cloud project.
        project_id (str): The ID of the Google Cloud project.
        model_name (str): The name of the model.
        publisher (str, optional): The publisher of the model. Defaults to "google".
        streaming (bool, optional): Whether to use streaming or not. Defaults to False.

    Returns:
        str: The endpoint URL.
    """
    base_url = f"https://{region}-aiplatform.googleapis.com/v1/"
    project_fragment = f"projects/{project_id}"
    location_fragment = f"locations/{region}"
    specifier = "streamRawPredict" if streaming else "rawPredict"
    model_fragment = f"publishers/{publisher}/models/{model_name}"
    url = f"{base_url}{'/'.join([project_fragment, location_fragment, model_fragment])}:{specifier}"
    return url

  def setup_client(self):
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
      **kwargs,
  ) -> str:
    """
    Makes a request to the Vertex AI API.

    Args:
        system_prompt (str): The system prompt.
        messages (list[dict]): The list of messages.
        model_params (Dict[str, Any] | None, optional): The list of model parameters. Defaults to None.
        **kwargs: Additional keyword arguments.

    Returns:
        str: The response from the API.
    """

    err = False
    err_msg = []
    if self.project_id is None:
      err_msg.append("[red]Google VertexAI: A Project ID must be configured for this connector.")
      err = True

    if self.region is None:
      err_msg.append("[red]Google VertexAI: A Region must be configured for this connector.")
      err = True

    if self.get_model().publisher is None:
      err_msg.append("Google VertexAI: The model publisher must be configured for this connector.")
      err = True

    if creds is None:
      err_msg.append("Google VertexAI: Credentials are missing.")
      err = True
    elif creds.token is None:
      err_msg.append("Google VertexAI: Credentials token is missing.")
      err = True

    if err:
      self.console_stderr.print(f"[red]{"\n".join(err_msg)}")
      raise Exception("\n".join(err_msg))

    is_streamed = False

    url = self.build_endpoint_url(
        project_id=self.project_id or "",
        region=self.region or "",
        model_name=self.get_model().key,
        publisher=self.get_model().publisher,  # type: ignore
        streaming=is_streamed,
    )

    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Accept": "application/json",
    }

    messages = [{"role": "system", "content": system_prompt}] + messages

    params = self.gen_params(model_params)
    params["model"] = self.get_model().key
    params["messages"] = messages

    # Make the call
    with httpx.Client() as client:
      import json

      resp = client.post(f"{url}", json=params, headers=headers, timeout=None)
      data = json.loads(resp.text)
      if self.debug:
        self.console_stderr.print(
            Panel(
                Syntax(
                    f"{json.dumps(data, indent=4)}",
                    "json",
                    word_wrap=True,
                ),
                title="[bold magenta]LLM Response",
                style="magenta",
            ),
        )
      if "object" in data and data["object"] == "Error":
        self.console_stderr.print(f"[red][bold]Google VertexAI: ERROR:[/bold] {data['message']}")
        raise Exception(f"Google VertexAI: ERROR: {data['message']}")

      return data["choices"][0]["message"]["content"]
