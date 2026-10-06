# Aanbiedingen-bot

Claude leest de aanbiedingen van winkels rond Eindhoven, vergelijkt ze met `items.yaml`
en meldt de goedkoopste deals op Discord. Er is **geen API-key** nodig: Claude zelf (een
Claude Code-sessie/routine) doet het lezen en matchen, de scripts doen de rest.

- `items.yaml` boodschappenlijst · `stores.yaml` winkels/bronnen
- `python -m bot.fetch URL` pagina ophalen met een echte browser (Playwright)
- `python -m bot.report offers.json [--dry-run]` ranken, prijsgeschiedenis, Discord
- `ROUTINE.md` de opdracht die Claude elke run uitvoert

## Setup
`pip install -r requirements.txt` (Chromium moet beschikbaar zijn, zie `CHROMIUM_PATH`).
Zet `DISCORD_WEBHOOK_URL` (Serverinstellingen → Integraties → Webhooks) als omgevingsvariabele
in de Claude-omgeving. Tests: `pytest`.

## Automatisch draaien (routine)
1. Zet in de Claude-omgeving de variabele `DISCORD_WEBHOOK_URL` (nooit in de repo of chat plakken).
2. Zet `scripts/setup-environment.sh` als Setup script van de omgeving.
3. De routine voert `ROUTINE.md` uit. AH en Kruidvat blokkeren servers: die doe je handmatig, zie `ROUTINE.md`.

## Kruidvat op je eigen computer
Kruidvat blokkeert cloud-servers, dus dit draait lokaal (de computer moet op het geplande moment aan staan).

Eenmalig:
```
git clone https://github.com/rubenyannicksmit1998-spec/Folder && cd Folder
pip install -r requirements.txt && playwright install chromium
# Claude Code installeren en inloggen: https://claude.com/claude-code  (gebruikt je abonnement, geen API-key)
# DISCORD_WEBHOOK_URL als omgevingsvariabele zetten
python -m bot.kruidvat_local --headed --dry-run   # eerst testen
```
Plannen (maandag 08:30):
- **Mac/Linux:** `crontab -e` → `30 8 * * 1 cd /pad/naar/Folder && python -m bot.kruidvat_local`
- **Windows:** Taakplanner → Basistaak → wekelijks maandag 08:30 → programma `python`,
  argumenten `-m bot.kruidvat_local`, starten in de map `Folder`.

Let op: de zoek-URL van Kruidvat in `stores.yaml` (`zoek_url`) is niet getest. Werkt `--dry-run` niet goed,
laat het me weten, dan pas ik hem aan op wat je computer te zien krijgt.
