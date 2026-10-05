# Aanbiedingen-bot

Leest folders/aanbiedingenpagina's van winkels rond Eindhoven, vergelijkt ze met `items.yaml`
en stuurt de goedkoopste deals naar Discord.

## Gebruik
1. Pas `items.yaml` (boodschappenlijst) en `stores.yaml` (bronnen) aan.
2. `pip install -r requirements.txt`
3. `ANTHROPIC_API_KEY=... python -m bot.main --dry-run` (print i.p.v. Discord)
4. Voor Discord: maak een webhook (Serverinstellingen → Integraties) en zet `DISCORD_WEBHOOK_URL`.
5. Automatisch: zet `ANTHROPIC_API_KEY` en `DISCORD_WEBHOOK_URL` als GitHub-secrets; de workflow draait ma/do.

Tests: `pytest`
