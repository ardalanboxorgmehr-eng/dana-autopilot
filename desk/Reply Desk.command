#!/bin/bash
# Double-click to open the Reply Desk. Close this window to stop it.
cd "$(dirname "$0")/.." || exit 1
git pull --rebase --autostash -q 2>/dev/null
exec python3 desk/app.py
