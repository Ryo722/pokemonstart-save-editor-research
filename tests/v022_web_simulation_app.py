"""NiceGUI user-simulation entry point; no server or private bytes embedded."""
import sys
from pathlib import Path
from nicegui import core as nicegui_core
import pokemonstart_v022_web as web

rom=Path(sys.argv[sys.argv.index('--rom')+1])

if nicegui_core.script_mode:
    if nicegui_core.script_client is not None:
        nicegui_core.script_client.delete()
        nicegui_core.script_client=None
    nicegui_core.script_mode=False
web.ui.run(root=lambda: web.create_page(rom),**web.server_options())
