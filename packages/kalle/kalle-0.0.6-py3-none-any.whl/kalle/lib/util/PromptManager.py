# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
from typing import Optional
from jinja2 import Template

from kalle.domain.PromptTemplate import PromptTemplate


class PromptManager:

  def __init__(
      self,
      config_manager,
      /,
      system_prompt_template: Optional[PromptTemplate] = None,
      system_prompt: Optional[str] = None,
      prompt_template: Optional[PromptTemplate] = None,
      piped_content: Optional[str] = None,
      param_content: Optional[str] = None,
      interaction_context: Optional[list] = None,
  ):
    self.config_manager = config_manager
    self.system_prompt_template = system_prompt_template
    self.system_prompt = system_prompt
    self.prompt_template = prompt_template
    self.piped_content = piped_content
    self.param_content = param_content
    self.interaction_context = interaction_context

  def compile_context(self):
    interaction_context = ""
    if self.interaction_context is not None:
      for c in self.interaction_context:
        interaction_context += f"\n{c}\n"
    return interaction_context

  def compile_prompt(self, prompt=None):
    final_prompt = prompt or self.param_content or ""
    if self.piped_content is not None:
      final_prompt = "\n\n---\n".join([final_prompt, self.piped_content])

    if self.prompt_template is not None and self.prompt_template.value is not None and self.prompt_template.value != "":
      template = Template(self.prompt_template.value)
      final_prompt = template.render(
          {
              "content": final_prompt,
              "prompt": final_prompt,
          }
      )

    return final_prompt

  def compile_system_prompt(self, prompt=None):
    final_prompt = self.config_manager.prompts["kalle_system_prompt"].value
    if prompt is not None:
      final_prompt = prompt
    elif self.system_prompt is not None:
      final_prompt = self.system_prompt
    if self.interaction_context is not None:
      final_prompt += f"\n\n{self.compile_context()}"

    if self.system_prompt_template is not None and self.system_prompt_template.value is not None:
      template = Template(self.system_prompt_template.value)
      final_prompt = template.render(
          {
              "system_prompt": final_prompt,
          }
      )

    return final_prompt

  def compile_tool_prompt(self, tools, prompt=None):
    final_prompt = self.config_manager.prompts["base_tool_prompt"].value or ""

    if prompt is not None:
      final_prompt = prompt

    for name, tool in tools.items():
      final_prompt += "\n\n" + tool.get_prompt()

    return final_prompt
