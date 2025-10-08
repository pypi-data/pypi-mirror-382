# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import unittest
from unittest.mock import MagicMock
from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.util.URIHandler import URIHandler
from kalle.domain.Uri import Uri

from transformers.utils import logging
import warnings

logging.disable_progress_bar()
warnings.filterwarnings("ignore")

os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""


class TestURIHandler(unittest.TestCase):

  def setUp(self):
    appname = "kalle"
    appauthor = "fe2"
    self.fixtures_dir = os.path.join(os.path.dirname(__file__), "../../fixtures")
    self.config_file = os.path.join(self.fixtures_dir, "config.yml")
    os.environ["HF_HOME"] = os.path.join(self.fixtures_dir, "cache/")
    os.environ["KALLE_CONFIG"] = self.config_file
    self.config_manager = ConfigManager(
        appname,
        appauthor,
        conversation_key="default",
        base_file_dir=self.fixtures_dir,
        use_conversation_history=False,
        debug=True,
    )
    self.uri_handler = URIHandler(self.config_manager, self.fixtures_dir)
    self.maxDiff = 1000

  def test_init(self):
    self.assertIsInstance(self.uri_handler.config_manager, ConfigManager)
    self.assertEqual(self.uri_handler.base_file_dir, self.fixtures_dir)

  def test_register_mime_loader(self):
    loader_function = MagicMock()
    self.uri_handler.register_mime_loader("test/mime", loader_function)
    self.assertIn("test/mime", self.uri_handler.mime_loader_functions)
    self.assertEqual(self.uri_handler.mime_loader_functions["test/mime"], loader_function)

  def test_parse_content(self):
    result = self.uri_handler.parse_content("This is a test")
    self.assertEqual(result, ("This is a test", {}))

  def test_load_mime_data_text(self):
    mime_type = "text/plain"
    data = b"Hello, World!"
    result = self.uri_handler.load_mime_data(mime_type, data)
    self.assertEqual(result, "Hello, World!")

  def test_load_mime_data_text_other(self):
    mime_type = "text/something"
    data = b"Hello, World!"
    result = self.uri_handler.load_mime_data(mime_type, data)
    self.assertEqual(result, "Hello, World!")

  def test_load_mime_data_html(self):
    mime_type = "text/html"
    with open(os.path.join(self.fixtures_dir, "test.html"), "rb") as f:
      data = f.read()
    result = self.uri_handler.load_mime_data(mime_type, data)
    self.assertEqual(
        result,
        "<html>\n<head>\n  <title>kalle test</title>\n</head>\n<body>\nThis is a test html file for the kalle unit tests.\n</body>\n</html>\n",
    )

  def test_load_mime_data_pdf(self):
    mime_type = "application/pdf"
    with open(os.path.join(self.fixtures_dir, "test.pdf"), "rb") as f:
      data = f.read()
    warnings.filterwarnings("ignore")
    result = self.uri_handler.load_mime_data(mime_type, data)
    self.assertEqual(result, "This is a test PDF for the kalle unit tests.")

  def test_load_mime_data_invalid(self):
    mime_type = "mime/invalid"
    data = b"Hello, World!"
    with self.assertRaises(ValueError):
      self.uri_handler.load_mime_data(mime_type, data)

  def test_extract_uris(self):
    text = "Hello, World! http://fe2.net https://fe2.net/anotherpage.html"
    updated_text, uri_dict = self.uri_handler.extract_uris(text)
    self.assertIsNotNone(updated_text)
    self.assertIsNotNone(uri_dict)
    self.assertIn("{URI_0}", uri_dict)
    self.assertEqual(
        uri_dict["{URI_0}"],
        Uri(uri="http://fe2.net", placeholder=None, error=None, mime_type=None, raw_content=None, content_filter=None),
    )
    self.assertIn("{URI_1}", uri_dict)
    self.assertEqual(
        uri_dict["{URI_1}"],
        Uri(
            uri="https://fe2.net/anotherpage.html",
            placeholder=None,
            error=None,
            mime_type=None,
            raw_content=None,
            content_filter=None,
        ),
    )

  def test_determine_file_type(self):
    uri = f'file:///{os.path.join(self.fixtures_dir, "test.pdf")}'
    result = self.uri_handler.determine_file_type(uri)
    self.assertIsNotNone(result)
    self.assertEqual(result, "application/pdf")

  def test_load_uri_contents_file(self):
    uri_dict = {"{URI_0}": Uri(uri="file://test.txt")}
    result = self.uri_handler.load_uri_contents(uri_dict)
    self.assertIsNotNone(result)
    self.assertEqual(
        result,
        {
            "{URI_0}": Uri(
                uri="file://test.txt",
                raw_content="This is a test text file for the kalle unit tests.\n",
                mime_type="text/plain",
            )
        },
    )

  def test_load_uri_contents_unregistered(self):
    uri_dict = {"{URI_0}": Uri(uri="file://test.png")}
    result = self.uri_handler.load_uri_contents(uri_dict)
    self.assertIsNotNone(result)
    self.assertEqual(result, {})

  def test_replace_placeholders(self):
    updated_dict = {
        "{URI_0}": Uri(
            uri="http://fe2.net",
            placeholder=None,
            error=None,
            mime_type=None,
            raw_content="Hello, world!",
            content_filter=None,
        )
    }
    original_content = "Hello, {URI_0}!"
    result = self.uri_handler.replace_placeholders(updated_dict, original_content)
    self.assertEqual(result, "Hello, <FILE=http://fe2.net>Hello, world!</FILE>\n!")

  def test_replace_placeholders_with_error(self):
    updated_dict = {
        "{URI_0}": Uri(
            uri="http://fe2.net",
            placeholder=None,
            error="Could not load url",
            mime_type=None,
            raw_content=None,
            content_filter=None,
        )
    }

    original_content = "Hello, {URI_0}!"
    with self.assertRaises(Exception) as context:
      self.uri_handler.replace_placeholders(updated_dict, original_content)
      self.assertEqual(str(context.exception), "One or more files not found")

  # fetch files for a few types

  def test_fetch_file_html(self):
    mime_type = "text/html"
    uri = Uri(uri="file://" + os.path.join(self.fixtures_dir, "test.html"), mime_type=mime_type)
    result = self.uri_handler.fetch_file(uri)
    self.assertIsNotNone(result)
    self.assertIn("<title>kalle test</title>", str(result.raw_content))
    self.assertIn("This is a test html file for the kalle unit tests.", str(result.raw_content))

  def test_fetch_file_text(self):
    mime_type = "text/plain"
    uri = Uri(uri="file://" + os.path.join(self.fixtures_dir, "test.txt"), mime_type=mime_type)
    result = self.uri_handler.fetch_file(uri)
    self.assertIsNotNone(result)
    self.assertIn("This is a test text file for the kalle unit tests.", str(result.raw_content))

  def test_fetch_file_pdf(self):
    mime_type = "application/pdf"
    uri = Uri(uri="file://" + os.path.join(self.fixtures_dir, "test.pdf"), mime_type=mime_type)
    result = self.uri_handler.fetch_file(uri)
    self.assertIsNotNone(result)
    self.assertIn("This is a test PDF for the kalle unit tests.", str(result.raw_content))

  def test_fetch_file_invalid(self):
    mime_type = "text/plain"
    uri = Uri(uri="file://" + os.path.join(self.fixtures_dir, "missing.txt"), mime_type=mime_type)
    result = self.uri_handler.fetch_file(uri)
    self.assertIsNotNone(result)
    self.assertIn("File not found: ", str(result.error))

  # loaders

  def test_load_text_plain(self):
    with open(os.path.join(self.fixtures_dir, "test.txt"), "rb") as f:
      data = f.read()
    result = self.uri_handler.load_text_plain(data)
    self.assertEqual(result, data.decode("utf-8"))

  def test_load_html(self):
    with open(os.path.join(self.fixtures_dir, "test.html"), "rb") as f:
      data = f.read()
    result = self.uri_handler.load_html(data)
    self.assertEqual(result, "\n\nkalle test\n\n\nThis is a test html file for the kalle unit tests.\n\n\n")

  def test_load_pdf(self):
    with open(os.path.join(self.fixtures_dir, "test.pdf"), "rb") as f:
      data = f.read()
    result = self.uri_handler.load_pdf(data)
    self.assertIsNotNone(result)
    self.assertIn("This is a test PDF for the kalle unit tests.", result)

  def test_load_pdf_debug_off(self):
    with open(os.path.join(self.fixtures_dir, "test.pdf"), "rb") as f:
      data = f.read()
    self.uri_handler.config_manager._debug = False
    result = self.uri_handler.load_pdf(data)
    self.assertIsNotNone(result)
    self.assertIn("This is a test PDF for the kalle unit tests.", result)

  # @TODO determine pattern for network based tests

  # def test_load_uri_contents_http(self):
  #    uri_dict = {'{URI_0}': 'http://fe2.net'}
  #    result = self.uri_handler.load_uri_contents(uri_dict)
  #    self.assertIsNotNone(result)

  # def test_parse_content(self):
  #    text = 'Hello, World! http://fe2.net'
  #    result = self.uri_handler.parse_content(text)
  #    self.assertIsNotNone(result)

  # def test_fetch_http(self):
  #    uri = 'http://localhost:18181/test.html'
  #    mime_type = 'text/plain'
  #    result = self.uri_handler.fetch_http('{URI_0}', mime_type, uri)
  #    self.assertIsNotNone(result)


if __name__ == "__main__":
  unittest.main()
