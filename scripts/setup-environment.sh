#!/usr/bin/env bash
# Zet de omgeving klaar voor de aanbiedingen-bot (plak dit in "Setup script" van de cloud-omgeving).
# Installeert Python-pakketten + certutil en laat Chromium de proxy-CA vertrouwen.
set -euo pipefail
pip install -q httpx PyYAML beautifulsoup4 pypdf playwright pytest
apt-get install -y -q libnss3-tools
mkdir -p "$HOME/.pki/nssdb"
[ -f "$HOME/.pki/nssdb/cert9.db" ] || certutil -N -d "sql:$HOME/.pki/nssdb" --empty-password
if [ -f /root/.ccr/agent-proxy-ca.crt ]; then
  certutil -A -d "sql:$HOME/.pki/nssdb" -n ccr-agent-proxy -t "C,," -i /root/.ccr/agent-proxy-ca.crt || true
fi
