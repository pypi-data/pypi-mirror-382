# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import io
import os
import re
import sys
import urllib.parse
import tempfile

import magic
import requests
from typing import Optional
from bs4 import BeautifulSoup

from kalle.domain.Uri import Uri
from kalle.lib.util.ConfigManager import ConfigManager

from rich.console import Console

console_stderr = Console(file=sys.stderr)


class URIHandler:

  def __init__(self, config_manager: ConfigManager, base_file_dir, /, console_stderr: Optional[Console] = None):
    self.config_manager = config_manager
    self.base_file_dir = base_file_dir
    self.console_stderr = console_stderr or Console(file=sys.stderr)

    self.mime_loader_functions = {}
    # @TODO update this to assume text unless its binary, use registered
    # types to identify non-text loaders
    self.register_mime_loader("application/octet-stream", self.load_text_plain)
    self.register_mime_loader("text", self.load_text_plain)
    self.register_mime_loader("text/plain", self.load_text_plain)
    self.register_mime_loader("text/html", self.load_text_plain)
    self.register_mime_loader("application/json", self.load_text_plain)
    self.register_mime_loader("application/javascript", self.load_text_plain)
    self.register_mime_loader("text/x-script.python", self.load_text_plain)
    self.register_mime_loader("application/postscript", self.load_text_plain)
    self.register_mime_loader("application/pdf", self.load_pdf)

  def register_mime_loader(self, mime_type, loader_function):
    self.mime_loader_functions[mime_type] = loader_function

  def load_mime_data(self, mime_type, data):
    if mime_type in self.mime_loader_functions:
      return self.mime_loader_functions[mime_type](data)
    elif mime_type.split("/")[0] in self.mime_loader_functions:
      return self.mime_loader_functions[mime_type.split("/")[0]](data)
    else:
      raise ValueError(f"Unsupported MIME type: {mime_type}")

  def parse_content(self, text) -> tuple[str, dict]:
    (content, uris) = self.extract_uris(text)

    uri_contents = self.load_uri_contents(uris)

    rendered_content = self.replace_placeholders(uri_contents, content)

    return (rendered_content, uris)

  def extract_uris(self, text):
    # Define the regex pattern for matching URIs
    uri_pattern = r"((file|https?)://(?:[^\s\\]|\\.)*)"

    # Find all matches in the text
    matches = re.findall(uri_pattern, text)

    # Extract and unquote the URIs
    uris = []

    for match in matches:
      uris.append(Uri(uri=match[0]))

    uri_dict = {}
    updated_text = text
    for i, uri in enumerate(uris):
      placeholder = f"{{URI_{i}}}"
      uri.uri = uri.uri.replace("\\ ", " ")
      uri_dict[placeholder] = uri
      updated_text = updated_text.replace(uri.uri, placeholder)

    return updated_text, uri_dict

  def determine_file_type(self, uri):
    parsed_uri = urllib.parse.urlparse(uri)

    mime_type = "application/octet-stream"  # Fallback type
    if parsed_uri.scheme == "file":
      path = os.path.expanduser(uri.replace("file://", ""))
      if not path.startswith("/"):
        path = f"{self.base_file_dir}/{path}"
      try:
        with open(path, "rb") as f:
          file_buffer = f.read(1024)  # Read a small chunk
          mime_type = magic.from_buffer(file_buffer, mime=True)
      except OSError:
        pass
    elif parsed_uri.scheme in ["http", "https"]:
      try:
        response = requests.get(uri, stream=True, timeout=5)
        file_buffer = io.BytesIO()
        for chunk in response.iter_content(1024):
          file_buffer.write(chunk)
          break  # Only need a small chunk for magic detection
        file_buffer.seek(0)
        _mime_type = magic.from_buffer(file_buffer.read(1024), mime=True)
        if _mime_type:
          mime_type = _mime_type
      except ConnectionResetError:
        return None
      except ImportError:
        pass

    return mime_type

  def load_uri_contents(self, uri_dict):
    updated_dict = {}
    for placeholder, uri in uri_dict.items():
      uri.mime_type = self.determine_file_type(uri.uri)

      # @TODO: this bypasses the checking in load_mime_data, preventing the
      # user from knowing that their file mime type is unsupported.
      if (
          uri.mime_type not in self.mime_loader_functions.keys()
          and uri.mime_type.split("/")[0] not in self.mime_loader_functions.keys()
      ):
        continue

      if uri.uri.startswith("file://"):
        self.console_stderr.print(f"[bold yellow]Fetching file: {uri.uri}")
        uri = self.fetch_file(uri)
      elif uri.uri.startswith(("http://", "https://")):
        self.console_stderr.print(f"[bold yellow]Loading url: {uri.uri}")
        uri = self.fetch_http(uri)

      updated_dict[placeholder] = uri

    return updated_dict

  def replace_placeholders(self, updated_dict, original_content):
    errors = False
    for placeholder, uri in updated_dict.items():
      if uri.error is not None:
        errors = True
        console_stderr.print(f"[red]ERROR: {uri.uri} can't be loaded: {uri.error}")
        replacement = uri.uri
      else:
        file_path = uri.uri
        file_path = file_path.replace("file://", "")
        # file_path = file_path.replace("http://", "")
        # file_path = file_path.replace("https://", "")
        replacement = f"<FILE={file_path}>{uri.raw_content}</FILE>\n"
      original_content = original_content.replace(placeholder, replacement)
    if errors:
      # exit after printing all the errors so the user can address everything
      # up front
      raise Exception("One or more files not found")
    return original_content

  def fetch_http(self, uri):
    # fetch contents and place into a var
    try:
      headers = {
          "User-Agent": "kalle url handler 0.1",
      }
      response = requests.get(uri.uri, headers=headers)
      response.raise_for_status()  # Raise an exception for bad status codes

      content = self.load_mime_data(uri.mime_type, response.content)

      uri.raw_content = content
    except requests.RequestException as e:
      uri.error = str(e)

    return uri

  def fetch_file(self, uri):
    # fetch contents and place into a var
    file_path = uri.uri.replace("file://", "")
    full_path = os.path.expanduser(file_path)
    if not full_path.startswith("/"):
      full_path = f"{self.base_file_dir}/{full_path}"

    if os.path.isfile(full_path):
      with open(full_path, "rb") as f:
        content = self.load_mime_data(uri.mime_type, f.read())

      uri.raw_content = content
    else:
      if self.config_manager.debug:
        console_stderr.print(f"[red]FILE NOT FOUND: -{file_path}-")
      uri.error = f"File not found: {file_path}"

    return uri

  # #########################################################################
  # LOADERS

  def load_text_plain(self, data):
    m = magic.Magic(mime_encoding=True)
    encoding = m.from_buffer(data)

    return data.decode(encoding)

  def load_html(self, data):
    soup = BeautifulSoup(data, "html.parser")
    content = soup.getText()

    return content

  def load_pdf(self, data):
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    # from docling_core.transforms.chunker import HierarchicalChunker

    with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
      tmp.write(data)
      tmp.flush()

      self.console_stderr.print("[bold yellow]Converting pdf")
      # we don't want printed errors or warnings unless we're in debug mode
      if not self.config_manager.debug:
        sys.stderr = open(os.devnull, "w")
      result = DocumentConverter(
          format_options={
              InputFormat.PDF: PdfFormatOption(
                  pipeline_options=PdfPipelineOptions(do_table_structure=True, generate_page_images=False)  # type: ignore
              )
          }
      ).convert(tmp.name)
      sys.stderr = sys.__stderr__

    return result.document.export_to_markdown()
