# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import os
import unittest
from kalle.lib.util.ConfigManager import ConfigManager
from kalle.lib.util.PromptManager import PromptManager
from kalle.lib.util.ToolHandler import ToolHandler
from kalle.domain.PromptTemplate import PromptTemplate


class TestPromptManager(unittest.TestCase):

  def setUp(self):
    appname = "kalle"
    appauthor = "fe2"
    self.fixtures_dir = os.path.join(os.path.dirname(__file__), "../../fixtures")
    self.config_file = os.path.join(self.fixtures_dir, "config.yml")
    os.environ["KALLE_CONFIG"] = self.config_file
    self.config = ConfigManager(
        appname, appauthor, conversation_key="default", base_file_dir=self.fixtures_dir, use_conversation_history=False
    )
    self.maxDiff = None

  def test_init(self):
    # ensure the Config object is ok
    self.assertEqual(
        self.config.prompts["kalle_system_prompt"].value,
        "Your name is Kalle. You are a helpful, confident, and friendly personal assistant.",
    )

  # CONTEXT
  def test_compile_context_none(self):
    prompt_manager = PromptManager(self.config)
    compiled_prompt = prompt_manager.compile_context()
    self.assertEqual(compiled_prompt, "")

  def test_compile_context(self):
    prompt_manager = PromptManager(self.config, interaction_context=["This is a test", "Second line"])
    compiled_prompt = prompt_manager.compile_context()
    self.assertEqual(compiled_prompt, "\nThis is a test\n\nSecond line\n")

  # SYSTEM PROMPT
  # test the base case of assuming the default configured system prompt
  def test_compile_system_prompt_with_config(self):
    prompt_manager = PromptManager(self.config)
    compiled_prompt = prompt_manager.compile_system_prompt()
    self.assertEqual(compiled_prompt, self.config.prompts["kalle_system_prompt"].value)

  # test the base case of assuming the default configured system prompt and a passed interaction context
  def test_compile_system_prompt_with_config_and_interaction_context(self):
    prompt_manager = PromptManager(self.config, interaction_context=["This is a test", "Second line"])
    compiled_prompt = prompt_manager.compile_system_prompt()
    self.assertEqual(
        compiled_prompt, str(self.config.prompts["kalle_system_prompt"].value) + "\n\n\nThis is a test\n\nSecond line\n"
    )

  # test the case where a system_prompt_template is specified
  def test_compile_system_prompt_with_system_prompt_template(self):
    system_prompt_template = PromptTemplate(value="Test system prompt template {{ system_prompt }}")
    system_prompt = "passed system prompt"
    prompt_manager = PromptManager(
        self.config, system_prompt_template=system_prompt_template, system_prompt=system_prompt
    )
    compiled_prompt = prompt_manager.compile_system_prompt()
    self.assertEqual(compiled_prompt, "Test system prompt template passed system prompt")

  # test the case where a prompt would be specified on the command line and stored when the prompt obj was created
  def test_compile_system_prompt_with_system_prompt(self):
    system_prompt = "Test system prompt override"
    prompt_manager = PromptManager(self.config, system_prompt=system_prompt)
    compiled_prompt = prompt_manager.compile_system_prompt()
    self.assertEqual(compiled_prompt, system_prompt)

  # test when we specify a custom prompt when compiling
  def test_compile_system_prompt_with_prompt(self):
    prompt_text = "Test prompt"
    prompt_manager = PromptManager(self.config)
    compiled_prompt = prompt_manager.compile_system_prompt(prompt=prompt_text)
    self.assertEqual(compiled_prompt, prompt_text)

  # PROMPT
  # test the case where a system_prompt_template is specified
  def test_compile_prompt_with_prompt_template(self):
    prompt_template = PromptTemplate(value="Test prompt template {{ content }}")
    param_content = "passed prompt"
    piped_content = "piped data"
    prompt_manager = PromptManager(
        self.config, prompt_template=prompt_template, param_content=param_content, piped_content=piped_content
    )
    compiled_prompt = prompt_manager.compile_prompt()
    self.assertEqual(compiled_prompt, "Test prompt template passed prompt\n\n---\npiped data")

  # test when we specify a custom prompt when compiling
  def test_compile_prompt_with_prompt(self):
    prompt_text = "Test prompt"
    prompt_manager = PromptManager(self.config)
    compiled_prompt = prompt_manager.compile_prompt(prompt=prompt_text)
    self.assertEqual(compiled_prompt, prompt_text)

  # TOOL PROMPT
  # test the base case of assuming the default configured tool prompt
  def test_compile_tool_prompt_with_config(self):
    prompt_manager = PromptManager(self.config)
    tool_handler = ToolHandler(self.config, base_file_dir=os.getcwd(), tool_list=["update_file"])
    tools = tool_handler.get_tools()
    compiled_prompt = prompt_manager.compile_tool_prompt(tools)
    self.assertEqual(
        compiled_prompt,
        'You are a tool calling agent.\n\nUse the function \'update_file\' to create, make, change or update a file with requested changes.\n    ONLY update a given file ONCE.\n\n    Place the file contents into the following form:\n    <body_contents=body_ref_id>contents here</body_contents>\n\n    NEVER PROVIDE PLACEHOLDERS AND INSTEAD USE 100% OF THE CONTENT THAT NEEDS TO EXIST IN THE FILE!!!\n\n    \n{\n    "type": "function",\n    "function": {\n        "name": "update_file",\n        "description": "Create, make, change or update the specified file with the new contents",\n        "parameters": {\n            "type": "object",\n            "properties": {\n                "path": {\n                    "type": "string",\n                    "description": "The path of the file, e.g., example/path/to/the/file.txt"\n                },\n                "body_ref": {\n                    "type": "string",\n                    "description": "The reference id to the associated body tag."\n                },\n                "required": ["path", "body_ref"]\n            }\n        }\n    }\n}\n\n    ',
    )

  def test_compile_tool_prompt_with_prompt(self):
    prompt_manager = PromptManager(self.config)
    tool_handler = ToolHandler(self.config, base_file_dir=os.getcwd(), tool_list=["update_file"])
    tools = tool_handler.get_tools()
    compiled_prompt = prompt_manager.compile_tool_prompt(tools, "Test tool prompt.")
    self.assertEqual(
        compiled_prompt,
        'Test tool prompt.\n\nUse the function \'update_file\' to create, make, change or update a file with requested changes.\n    ONLY update a given file ONCE.\n\n    Place the file contents into the following form:\n    <body_contents=body_ref_id>contents here</body_contents>\n\n    NEVER PROVIDE PLACEHOLDERS AND INSTEAD USE 100% OF THE CONTENT THAT NEEDS TO EXIST IN THE FILE!!!\n\n    \n{\n    "type": "function",\n    "function": {\n        "name": "update_file",\n        "description": "Create, make, change or update the specified file with the new contents",\n        "parameters": {\n            "type": "object",\n            "properties": {\n                "path": {\n                    "type": "string",\n                    "description": "The path of the file, e.g., example/path/to/the/file.txt"\n                },\n                "body_ref": {\n                    "type": "string",\n                    "description": "The reference id to the associated body tag."\n                },\n                "required": ["path", "body_ref"]\n            }\n        }\n    }\n}\n\n    ',
    )


if __name__ == "__main__":
  unittest.main()
