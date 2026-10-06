# Aanbiedingen-bot (lokaal)

Draait op je eigen computer (thuis-IP, dus winkels blokkeren je niet). Per winkel haalt een browser de
aanbiedingen op (AH via de app-API), je lokale Claude Code (`claude -p`, je eigen abonnement, **geen
API-key**) kiest wat bij `items.yaml` past, en de beste deals gaan naar Discord. Prijsgeschiedenis staat
in `data/prijzen.sqlite`.

## Installeren (eenmalig)
Vooraf: Python 3.11+ en [Claude Code](https://claude.com/claude-code) (ingelogd). Dan, in de map van deze repo:
- **Mac/Linux:** `bash scripts/install-local.sh`
- **Windows:** `powershell -ExecutionPolicy Bypass -File scripts\install-local.ps1`

Het script installeert alles, vraagt je Discord-webhook en plant elke maandag 08:30 een run
(de computer moet dan aan staan). Test eerst: `python -m bot.local_run --headed --dry-run`.

## Aanpassen
- `items.yaml` boodschappenlijst (optioneel `max_prijs`, `opmerking`)
- `stores.yaml` winkels en pagina's. Eén winkel testen: `--only Lidl`.
- Webhook staat in `.env.local` (niet in git) of als omgevingsvariabele `DISCORD_WEBHOOK_URL`.

Onderdelen: `bot/local_run.py` (run), `bot/ah.py` (AH-API), `bot/report.py` (ranken + Discord),
`bot/history.py` (prijsgeschiedenis). Tests: `pytest`.
