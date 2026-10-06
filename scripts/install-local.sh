#!/usr/bin/env bash
# Mac/Linux: installeert alles voor de lokale Kruidvat-run en plant hem elke maandag 08:30.
# Gebruik:  bash scripts/install-local.sh        (vanuit de Folder-map)
set -euo pipefail
cd "$(dirname "$0")/.."
command -v python3 >/dev/null || { echo "Installeer eerst Python 3.11+"; exit 1; }
command -v claude >/dev/null || { echo "Installeer eerst Claude Code (https://claude.com/claude-code) en log in"; exit 1; }
python3 -m venv .venv && . .venv/bin/activate
pip install -q -r requirements.txt && playwright install chromium
read -rsp "Plak je Discord-webhook-URL (blijft onzichtbaar): " HOOK; echo
umask 077; printf 'DISCORD_WEBHOOK_URL=%s\n' "$HOOK" > .env.local   # staat in .gitignore
RUN="cd $PWD && set -a && . ./.env.local && set +a && . .venv/bin/activate && python -m bot.kruidvat_local >> kruidvat.log 2>&1"
( crontab -l 2>/dev/null | grep -v kruidvat_local; echo "30 8 * * 1 $RUN" ) | crontab -
echo "Klaar. Test nu: .venv/bin/python -m bot.kruidvat_local --headed --dry-run"
