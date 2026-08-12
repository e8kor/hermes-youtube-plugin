#!/usr/bin/env bash
# Install the youtube Hermes plugin.
#   ./install.sh          # copy plugin into ~/.hermes/plugins and install deps
#   ./install.sh --no-deps# only copy the plugin, skip dependency install
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
PLUGIN_NAME="youtube"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/plugin"
DEST_DIR="$HERMES_HOME/plugins/$PLUGIN_NAME"

echo "==> Installing $PLUGIN_NAME plugin"
mkdir -p "$HERMES_HOME/plugins"
rm -rf "$DEST_DIR"
cp -r "$SRC_DIR" "$DEST_DIR"
echo "    Copied plugin to $DEST_DIR"

# Find the hermes venv (or use python3)
VENV="$HERMES_HOME/hermes-agent/venv"
PY=python3
if [ -x "$VENV/bin/python" ]; then
  PY="$VENV/bin/python"
fi

if [ "${1:-}" != "--no-deps" ]; then
  echo "==> Installing dependencies: google-api-python-client google-auth"
  for dep in google-api-python-client google-auth; do
    "$PY" -m pip install "$dep" 2>/dev/null || "$PY" -m pip install "$dep" --quiet
  done
  echo "    Dependencies installed."
fi

echo
echo "==> Enable the plugin (takes effect next session):"
echo "    hermes plugins enable $PLUGIN_NAME"

echo "==> Cron / scheduler:"
echo "None (read-only status/subs/feed tools)."
echo
echo "Done. Restart Hermes (/exit then hermes) for the plugin to load."
