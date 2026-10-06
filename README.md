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
