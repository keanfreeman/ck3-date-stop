#!/usr/bin/env bash
# Copies mod/ into CK3's local mod folder and writes the .mod file the CK3
# launcher looks for (it finds mods through ./mod/*.mod, not folder scanning).
# Re-run after every change.
set -euo pipefail
src="$(cd "$(dirname "$0")/.." && pwd)/mod/"
base="${CK3_MOD_DIR:-$HOME/.local/share/Paradox Interactive/Crusader Kings III/mod}"
dest="$base/Date Stop"
[ -L "$dest" ] && rm "$dest"
mkdir -p "$dest"
rsync -a --delete "$src" "$dest/"
{ cat "$src/descriptor.mod"; echo "path=\"$dest\""; } > "$base/date_stop_ck3.mod"
echo "installed to $dest"
