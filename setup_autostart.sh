#!/bin/bash
# Option A: start dictate.py at login via Terminal (which already has Mic, Input
# Monitoring and Accessibility permissions), then hide Terminal.
#
# Usage (run from the folder that contains dictate.py):
#   bash setup_autostart.sh              # install + start now
#   bash setup_autostart.sh --uninstall  # stop + remove

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$HOME/dictate-env/bin/python3"
LOG="$HOME/Library/Logs/dictate.log"
LAUNCHER="$HOME/Applications/DictateLauncher.app"
OLD_APP="$HOME/Applications/Dictate.app"

remove_login_item() {
  osascript -e "tell application \"System Events\" to delete login item \"$1\"" 2>/dev/null || true
}

# Clean up the earlier Dictate.app attempt (it cannot get mic access)
pkill -f dictate.py 2>/dev/null || true
remove_login_item "Dictate"
rm -rf "$OLD_APP"
tccutil reset All local.dictate >/dev/null 2>&1 || true   # drop old Dictate.app permission entries
rm -f "$SCRIPT_DIR/install_dictate_app.sh"

if [[ "${1:-}" == "--uninstall" ]]; then
  remove_login_item "DictateLauncher"
  rm -rf "$LAUNCHER"
  echo "Removed DictateLauncher and stopped dictation."
  exit 0
fi

[[ -f "$SCRIPT_DIR/dictate.py" ]] || { echo "dictate.py not found in $SCRIPT_DIR"; exit 1; }
[[ -x "$VENV_PY" ]] || { echo "Python venv not found at $VENV_PY"; exit 1; }
mkdir -p "$HOME/Applications" "$(dirname "$LOG")"

# Shell command Terminal runs: start only if not already running, detach, close shell
CMD="pgrep -f dictate.py >/dev/null || (cd '$SCRIPT_DIR' && nohup '$VENV_PY' -u dictate.py >> '$LOG' 2>&1 &); exit"

APPLESCRIPT="$(mktemp -d)/launcher.applescript"
cat > "$APPLESCRIPT" <<EOF
tell application "Terminal"
    do script "$CMD"
end tell
delay 2
tell application "System Events"
    set visible of application process "Terminal" to false
end tell
EOF

rm -rf "$LAUNCHER"
osacompile -o "$LAUNCHER" "$APPLESCRIPT"
rm -rf "$(dirname "$APPLESCRIPT")"

echo "Adding DictateLauncher to Login Items ..."
remove_login_item "DictateLauncher"
if ! osascript -e "tell application \"System Events\" to make login item at end with properties {path:\"$LAUNCHER\", hidden:true}" >/dev/null; then
  echo "Could not add automatically. Add manually:"
  echo "  System Settings > General > Login Items > + > $LAUNCHER"
fi

sleep 2
: > "$LOG"
echo "Starting now ..."
open "$LAUNCHER"

cat <<EOF

Done.
- First run: allow "DictateLauncher" to control Terminal and System Events.
- Check:   sleep 10; cat "$LOG"      (expect "Ready...")
- Stop:    pkill -f dictate.py
- Start:   open "$LAUNCHER"
- Remove:  bash setup_autostart.sh --uninstall
Note: keep Terminal running (hidden is fine). If you quit Terminal, run the Start command again.
EOF
