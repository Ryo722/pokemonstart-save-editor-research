#!/bin/bash
# PokemonStart v0.22 Editor — Mac launcher (double-click in Finder, or run in Terminal).
# Usage: ./start-editor.command [/path/inside/PokemonStart-private/exact-v022.gba]
# Serves only on http://127.0.0.1:8766 and opens it in the default browser.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  echo "初回セットアップ: Python 仮想環境を作成して NiceGUI を導入します..."
  python3 -m venv .venv
  .venv/bin/python -m pip install --quiet -r requirements-m4-ui.txt
fi

ROM_ARGS=()
ROM="${1:-${POKEMONSTART_ROM:-}}"
if [ -n "$ROM" ]; then
  ROM_ARGS=(--rom "$ROM")
fi

echo "PokemonStart v0.22 Editor を起動します: http://127.0.0.1:8766  (終了: Ctrl+C)"
exec .venv/bin/python pokemonstart_v022_product_web.py "${ROM_ARGS[@]+"${ROM_ARGS[@]}"}" --open
