"""NiceGUI user-simulation entry point; inputs arrive only via test argv."""
import argparse
from pathlib import Path

from nicegui import core as nicegui_core
import pokemonstart_m4_web as web

parser = argparse.ArgumentParser()
parser.add_argument("--journal", type=Path, required=True)
parser.add_argument("--rom", type=Path, required=True)
parser.add_argument("--environment", required=True)
args = parser.parse_args()
# NiceGUI's script-mode probe can create a pseudo client before test startup.
# The adapter itself constructs every element inside the root page function.
if nicegui_core.script_mode:
    if nicegui_core.script_client is not None:
        nicegui_core.script_client.delete()
        nicegui_core.script_client = None
    nicegui_core.script_mode = False
web.ui.run(root=lambda: web.create_page(args.journal, args.rom, args.environment),
           **web.server_options())
