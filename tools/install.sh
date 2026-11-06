#!/usr/bin/env bash
# Copies mod/ into CK3's local mod folder as "CK3 Date Stop" (the name the launcher
# gave it when it was uploaded to the Workshop) and writes the .mod file the launcher
# looks for (it finds mods through ./mod/*.mod, not folder scanning).
# Re-run after every change, and restart the game: GUI files load at startup.
set -euo pipefail
src="$(cd "$(dirname "$0")/.." && pwd)/mod/"
base="${CK3_MOD_DIR:-$HOME/.local/share/Paradox Interactive/Crusader Kings III/mod}"
dest="$base/CK3 Date Stop"
[ -L "$dest" ] && rm "$dest"
mkdir -p "$dest"
rsync -a --delete "$src" "$dest/"
{ cat "$src/descriptor.mod"; echo; echo "path=\"$dest\""; } > "$base/CK3 Date Stop.mod"
echo "installed to $dest"
