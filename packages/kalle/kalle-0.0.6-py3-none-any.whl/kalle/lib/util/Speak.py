# kalle
# Copyright (C) 2024-2025 Wayland Holdings, LLC
# vim: ft=python et sw=2
import re
import sys

import asyncio
import websockets
import json

from typing import Optional
from rich.console import Console


class Speak:

  def __init__(self, config, /, console_stderr: Optional[Console] = None):
    self.config = config
    self.console_stderr = console_stderr or Console(file=sys.stderr)

  async def say(self, text):
    # Replace 'Kalle' or 'kalle' with a phonetic version
    speak_text = re.sub(r"\n", " ", text, re.DOTALL)
    speak_text = re.sub(r"Kalle|kalle", "Kal-lee", speak_text, re.DOTALL)
    speak_text = re.sub(r"[*]+", "", speak_text, re.DOTALL)
    speak_text = re.sub(r"<[^>]*>", "", speak_text, re.DOTALL)
    speak_text = re.sub(r"<[^>]*$", "", speak_text, re.DOTALL)

    try:
      uri = self.config["voicebox_uri"]
      async with websockets.connect(uri) as websocket:
        # Prepare the request data
        request_data = {
            "text": speak_text,
            "voice": self.config["voice"],
            "speed": self.config["speed"],
            "api_key": self.config["api_key"],
        }

        # Send the request
        await websocket.send(json.dumps(request_data))

        # Listen for responses while keeping the connection alive
        try:
          while True:
            # Keep the connection alive
            await websocket.send("")
            await asyncio.sleep(0.1)

        except asyncio.TimeoutError:
          # This is expected when waiting for messages with a timeout
          pass
        except websockets.exceptions.ConnectionClosed:
          # Connection was closed by the server
          pass

    except Exception as e:
      self.console_stderr.print(f"[red]An error occurred while attempting to speak: {e}")
      if self.config.get("debug", False):
        self.console_stderr.print_exception(show_locals=True)
