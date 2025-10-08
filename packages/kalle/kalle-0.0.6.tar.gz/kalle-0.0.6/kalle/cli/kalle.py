# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2

# #############################################################################
# Imports
# #############################################################################
from rich.box import HORIZONTALS, ROUNDED
from rich.markdown import Markdown
from rich.rule import Rule
import kalle.cli.sigint_clean_exit  # noqa: F401  Imported for side effect

import argparse
import asyncio
import json
import os
import sys
import traceback

from platformdirs import user_config_dir, user_data_dir, user_cache_dir
from rich.panel import Panel
from rich_argparse import RawDescriptionRichHelpFormatter

from kalle.lib.Kalle import Kalle


def load_gbnf_file(kalle: Kalle, path: str):
  path = os.path.expanduser(path)
  if not path.startswith("/"):
    jsonschema_path = os.path.join(kalle.base_file_dir, path)
  try:
    with open(path, "r") as f:
      return f.read()
  except FileNotFoundError:
    kalle.console_stderr.print(f"[red]Could not find GBNF file {path}")
    sys.exit(31)
  except IsADirectoryError:
    kalle.console_stderr.print(f"[red]Specified GBNF path '{path}' is a directory")
    sys.exit(32)
  except Exception as e:
    kalle.console_stderr.print(f"[red]Unspecified error loading GBNF file '{path}': {e}")
    sys.exit(34)


def load_json_schema(kalle: Kalle, jsonschema_path: str):
  jsonschema_path = os.path.expanduser(jsonschema_path)
  if not jsonschema_path.startswith("/"):
    jsonschema_path = os.path.join(kalle.base_file_dir, jsonschema_path)
  try:
    with open(jsonschema_path, "r") as f:
      return json.dumps(json.loads(f.read()))
  except FileNotFoundError:
    kalle.console_stderr.print(f"[red]Could not find JSON schema {jsonschema_path}")
    sys.exit(31)
  except IsADirectoryError:
    kalle.console_stderr.print(f"[red]Specified JSON schema path '{jsonschema_path}' is a directory")
    sys.exit(32)
  except json.decoder.JSONDecodeError as e:
    kalle.console_stderr.print(f"[red]Invalid JSON schema '{jsonschema_path}': {e}")
    sys.exit(33)
  except Exception as e:
    kalle.console_stderr.print(f"[red]Unspecified error loading JSON schema '{jsonschema_path}': {e}")
    sys.exit(34)


def parse_args():
  parser = argparse.ArgumentParser(
      prog="kalle",
      description="[yellow]I'm Kalle! A smart cli friend",
      formatter_class=RawDescriptionRichHelpFormatter,
  )
  RawDescriptionRichHelpFormatter.styles["argparse.prog"] = "yellow"

  parser.add_argument("-l", "--list_conversations", action="store_true", help="List conversations")
  parser.add_argument(
      "-c",
      "--conversation",
      type=str,
      default=None,
      help="Use a specific conversation",
  )
  parser.add_argument(
      "--long-conversation-handling",
      type=str,
      default=None,
      help="How to handle long conversations when sending context to the LLM (none, truncate, summarize)",
  )
  parser.add_argument(
      "-i",
      "--interactive",
      action="store_true",
      help="Have an interactive conversation (don't return immediately to the prompt)",
  )
  parser.add_argument("-H", "--history", action="store_true", help="Show the conversation history")
  parser.add_argument(
      "-x",
      "--no_conversation_history",
      action="store_true",
      help="Don't include the conversation history",
  )
  parser.add_argument("-z", "--unformat", action="store_true", help="Remove output formatting")

  parser.add_argument(
      "-E",
      "--embed",
      action="store_true",
      help="Generate an embedding for the content (returns json)",
  )
  parser.add_argument(
      "-S",
      "--store",
      action="store_true",
      help="Store the contents provided via piped or cli prompt in memory",
  )
  parser.add_argument("-Q", "--query", action="store_true", help="Query the memory store")
  parser.add_argument(
      "-M",
      "--use_memory",
      action="store_true",
      help="Use the memory store to enhance the request",
  )
  parser.add_argument(
      "-R",
      "--doc_reference",
      type=str,
      help="Document reference to be included when storing content in memory",
  )
  parser.add_argument("-K", "--knowledgebase", type=str, help="Name of the memory store to use.")

  parser.add_argument("-s", "--system_prompt", type=str, help="Override the default system prompt")
  parser.add_argument("-V", "--use_voice", action="store_true", help="Speak the response")
  parser.add_argument(
      "-f",
      "--follow",
      action="store_true",
      help=(
          "Follow [grey58]http(s)://[/grey58] and [grey58]file://[/grey58] URIS and include their contents (only in the cli prompt, not piped input)"
      ),
  )
  parser.add_argument(
      "-F",
      "--follow-all",
      action="store_true",
      help=(
          "Follow [grey58]http(s)://[/grey58] and [grey58]file://[/grey58] URIS and include their contents (in both cli prompt and piped input)"
      ),
  )

  parser.add_argument(
      "--jsonschema",
      type=str,
      help=(
          "Specifiy the path to a JSON schema to constrain the output [italic](TabbyAPI, Llama.cpp, Ollama only)[/italic]"
      ),
  )
  parser.add_argument(
      "--regex",
      type=str,
      help="Specifiy a regex to constrain the output [italic](TabbyAPI)[/italic]",
  )
  parser.add_argument(
      "--gbnf",
      type=str,
      help="Specifiy a gbnd file to constrain the output",
  )
  parser.add_argument("-D", "--dir", type=str, help="Base dir for [grey58]file:://[/grey58] URIs")

  parser.add_argument("-P", "--profile", type=str, default=None, help="Set the profile to use")
  parser.add_argument(
      "-b",
      "--base",
      action="store_true",
      help="Use the [grey58]base[/grey58] profile",
  )
  parser.add_argument(
      "-.",
      "--tiny",
      action="store_true",
      help="Use the [grey58]tiny[/grey58] profile",
  )
  parser.add_argument(
      "-C",
      "--code",
      action="store_true",
      help="Use the [grey58]code[/grey58] profile",
  )

  parser.add_argument("-X", "--tabbyapi", action="store_true", help="Use [grey58]TabbyAPI[/grey58]")
  parser.add_argument("-o", "--ollama", action="store_true", help="Use [grey58]Ollama[/grey58]")
  parser.add_argument(
      "-A",
      "--anthropic",
      action="store_true",
      help="Use [grey58]Anthropic's[/grey58] API",
  )
  parser.add_argument("-O", "--openai", action="store_true", help="Use [grey58]OpenAI[/grey58] API")
  parser.add_argument("-G", "--groq", action="store_true", help="Use [grey58]Groq[/grey58] API")
  parser.add_argument(
      "--vertexai",
      action="store_true",
      help="Use [grey58]Google VertexAI[/grey58] API",
  )

  parser.add_argument("-p", "--pattern", type=str, default=None, help="Set the pattern to use")

  parser.add_argument(
      "-t",
      "--tool",
      default=None,
      nargs="*",
      type=str,
      help="Enable tool calling with optional comma separated values (e.g., tool1,tool2)",
  )

  parser.add_argument("-m", "--model", type=str, help="Model to use (if applicable)")
  parser.add_argument("--temp", type=str, help="Temperature to use for the model")
  parser.add_argument("--seed", type=str, help="Seed to use for inference (if applicable)")
  parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
  parser.add_argument(
      "prompt",
      nargs=argparse.REMAINDER,
      help="The message for [yellow]kalle[/yellow]",
  )

  parser.epilog = f"[bold cyan]Config directory:[/bold cyan] [grey58]{user_config_dir('kalle', 'fe2')}\n"
  parser.epilog += f"[bold cyan]Data directory:[/bold cyan] [grey58]{user_data_dir('kalle', 'fe2')}\n"
  parser.epilog += (
      f"[bold cyan]Conversations directory:[/bold cyan] [grey58]{user_data_dir('kalle', 'fe2')}/conversations\n"
  )
  parser.epilog += f"[bold cyan]Cache directory:[/bold cyan] [grey58]{user_cache_dir('kalle', 'fe2')}/conversations"

  return parser.parse_args()


def process_args(profile_keys: list[str], **kwargs):
  # map args to vars
  param_content = " ".join(kwargs.get("prompt", []))
  param_content = param_content.lstrip("-- ")

  # coalesce the shortcut flags + -P lag into the args_profile_key output value
  profile_key = None
  if "profile" in kwargs:
    profile_key = kwargs.get("profile", None)

  if profile_key is None:
    for arg in profile_keys:
      if arg in kwargs.keys() and kwargs[arg]:
        profile_key = arg
        break

  follow = None
  if kwargs.get("follow", False):
    follow = "prompt"
  if kwargs.get("follow_all", False):
    follow = "all"

  return {
      "use_conversation_history": not kwargs.get("noconversationhistory", False),
      "long_conversation_handling": kwargs.get("long_conversation_handling", None),
      "interactive": kwargs.get("interactive", None),
      "format_output": not kwargs.get("unformat", False),
      "embed": kwargs.get("embed", False),
      "store": kwargs.get("store", False),
      "knowledgebase": kwargs.get("knowledgebase", None),
      "doc_reference": kwargs.get("doc_reference", None),
      "query": kwargs.get("query", False),
      "use_memory": kwargs.get("use_memory", False),
      "use_voice": kwargs.get("use_voice", False),
      "conversation_key": kwargs.get("conversation", None),
      "args_system_prompt": kwargs.get("system_prompt", None),
      "args_profile_key": profile_key,
      "args_pattern_key": kwargs.get("pattern", None),
      "follow_uris": follow,
      "tool_list": kwargs.get("tool", None),
      "use_tools": True if kwargs.get("tool", None) is not None else False,
      "args_model_string": kwargs.get("model", None),
      "debug": kwargs.get("debug", False),
      "param_content": param_content,
  }


def cli():
  args = parse_args()
  debug = args.debug
  kalle = Kalle(base_file_dir=args.dir)

  param_content = " ".join(args.prompt)
  param_content = param_content.lstrip("-- ")

  # Check if data is piped in
  piped_content = None
  if not sys.stdin.isatty():
    piped_content = sys.stdin.read()

  try:
    # #############################################################################################################
    # Do things that can cause us to exit early

    # if we're just listing conversations, do that and exit early
    if args.list_conversations:
      kalle.list_conversations()
      sys.exit(0)

    # show history and exit early
    if args.history:
      kalle.show_history(args.conversation, not args.unformat)
      sys.exit(0)

    # exit early if we've specified multiple constrainer types
    constrainer_count = 0
    constrainer_count += 1 if args.regex is not None else 0
    constrainer_count += 1 if args.jsonschema is not None else 0
    constrainer_count += 1 if args.gbnf is not None else 0
    if constrainer_count > 1:
      kalle.console_stderr.print("[red]Specify only one of JSON schema or regex")
      sys.exit(2)

    # exit early if we haven't specified a request
    if param_content == "" and piped_content is None and args.pattern is None and not args.interactive:
      kalle.console_stderr.print("[red]Need a request")
      sys.exit(1)

    # exit early if too many profiles are specified
    args_profiles = []
    for arg in kalle.config_manager.config.profiles.keys():
      if vars(args).get(arg, False):
        args_profiles.append(arg)

    if len(args_profiles) > 1:
      kalle.console_stderr.print(
          f"[red][bold]Too many profiles specified ([/bold][italic]{', '.join(args_profiles)}[/italic][bold]) choose only one"
      )
      sys.exit(4)

    kwargs = process_args(profile_keys=list(kalle.config_manager.config.profiles.keys()), **vars(args))
    kwargs["piped_content"] = piped_content

    # extract the model params if passed
    args_model_params = {}
    if args.temp is not None:
      args_model_params["temperature"] = args.temp
    if args.seed is not None:
      args_model_params["seed"] = args.seed
    kwargs["args_model_params"] = args_model_params

    # extract the constrainer if available in the cli args
    constrainer = None
    if args.regex is not None:
      from kalle.domain.Constrainer import Constrainer, ConstrainerType

      constrainer = Constrainer(
          type=ConstrainerType("regex"),
          value=args.regex,
      )

    elif args.jsonschema is not None:
      from kalle.domain.Constrainer import Constrainer, ConstrainerType

      constrainer = Constrainer(
          type=ConstrainerType("jsonschema"),
          value=load_json_schema(kalle, args.jsonschema),
      )
    elif args.gbnf is not None:
      from kalle.domain.Constrainer import Constrainer, ConstrainerType

      constrainer = Constrainer(
          type=ConstrainerType("gbnf"),
          value=load_gbnf_file(kalle, args.gbnf),
      )
    kwargs["constrainer"] = constrainer

    if not args.interactive:
      asyncio.run(kalle.run(**kwargs))
    else:
      if kwargs["piped_content"] is not None:
        kalle.console_stderr.print("[bold red]Interactive mode can't be used with piped input")
        sys.exit(6)

      from .prompt import CliPrompt

      from kalle.lib.util.ToolHandler import ToolHandler

      tool_handler = ToolHandler(kalle.config_manager, ".")
      all_tools = list(tool_handler.get_tools().keys())
      prompt_history = []
      panel_format = ROUNDED
      if kalle.config_manager.config.interactive_style == "lines":
        panel_format = HORIZONTALS

      kalle.conversing = True
      if (
          kalle.config_manager.config.interactive_style != "plain"
          and not args.unformat
          and kwargs["conversation_key"] is not None
      ):
        kalle.show_history(kwargs["conversation_key"], not args.unformat)

      # start a conversation loop
      while kalle.conversing:
        error = None
        if kwargs["param_content"] is not None and kwargs["param_content"] != "":
          try:
            asyncio.run(kalle.run(**kwargs))
          except Exception as e:
            # Capture the error message and traceback
            error_type = type(e).__name__
            error_message = str(e)
            if debug:
              error_traceback = traceback.format_exc()
              error = f"{error_type}: {error_message}\n\nTraceback:\n{error_traceback}"
            else:
              error = f"{error_type}: {error_message}"
            kalle.console_stderr.print(f"[red]ERROR: {error_type}: {error_message}")

        prompt = ""
        if kalle.config_manager.config.interactive_style != "plain" and kwargs["format_output"]:
          while prompt == "":
            prompt_input = CliPrompt(
                profile_name=kwargs.get("args_profile_key", None),
                conversation_dir=kalle.config_manager.conversation_dir,
                follow_uris=kwargs["follow_uris"],
                all_tools=all_tools,
                use_tools=kwargs["use_tools"],
                use_voice=kwargs["use_voice"],
                tool_list=kwargs["tool_list"],
                format_output=kwargs["format_output"],
                conversation_key=kwargs["conversation_key"],
                long_conversation_handling=kwargs["long_conversation_handling"],
                pattern_key=kwargs["args_pattern_key"],
                debug=kwargs["debug"],
                error=error,
            )
            res = prompt_input.run(inline=True, mouse=False)
            if res is None or res == -1:
              sys.exit(0)
            if prompt_input.conversation_key is not None and kwargs["conversation_key"] is None:
              # if we've added a conversation key, we want to persist immediately
              kwargs["conversation_key"] = prompt_input.conversation_key
              if hasattr(kalle, "conversation"):
                kalle.conversation_tools.persist_conversation(
                    kalle.conversation,
                    conversation_key=prompt_input.conversation_key,
                )
            if prompt_input.value is not None:
              prompt = prompt_input.value.strip()
              kwargs["follow_uris"] = prompt_input.follow_uris
              kwargs["format_output"] = prompt_input.format_output
              kwargs["tool_list"] = prompt_input.tool_list
              kwargs["use_tools"] = prompt_input.use_tools
              kwargs["use_voice"] = prompt_input.use_voice
              kwargs["conversation_key"] = prompt_input.conversation_key
              kwargs["debug"] = prompt_input.kalle_debug
        else:
          prompt = kalle.console.input("[yellow bold]ツ> ")

        kwargs["param_content"] = prompt
        if kalle.config_manager.config.interactive_style == "lines":
          kalle.console.print(
              Rule(style="blue"),
          )
          print(prompt)
          kalle.console.print(
              Rule(title="[blue bold]─ [white]< User >[/white]", align="left", style="blue"),
          )
        elif kalle.config_manager.config.interactive_style == "bubble":
          if kwargs["format_output"]:
            kalle.console.print(
                Panel(
                    prompt,
                    box=panel_format,
                    subtitle="[white bold]< User >",
                    subtitle_align="right",
                    border_style="blue",
                )
            )

        prompt_history.append(prompt)
  except EOFError:
    sys.exit(0)
  except Exception as e:
    kalle.console_stderr.print(f"[red]An error occurred: {e=}")
    if debug:
      kalle.console_stderr.print_exception()
    sys.exit(99)


if __name__ == "__main__":
  cli()
