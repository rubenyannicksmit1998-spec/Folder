# Opdracht voor de wekelijkse run (Claude doet het uitlezen zelf, geen API-key nodig)

1. Lees `items.yaml` en `stores.yaml`.
2a. Albert Heijn: `python -m bot.ah ah_offers.json` (app-API, werkt wel vanaf servers). Beoordeel de
   resultaten en neem alleen producten die echt bij het item passen over in `offers.json`.
2. Voor elke winkel zonder `status: geblokkeerd` en zonder `status: api` en voor elke bron-URL:
   `python -m bot.fetch <url>` (echte browser, JavaScript uitgevoerd).
   Mislukt het? Sla de winkel over en noteer dat in de samenvatting.
3. Lees de tekst zelf en zoek aanbiedingen die echt bij een item uit `items.yaml` passen
   (zelfde soort product, houd rekening met `opmerking`). Verzin nooit prijzen. Sla producten
   over die "niet verkrijgbaar" zijn. Bij "2 voor €5" reken je om naar prijs per stuk.
4. Schrijf alles naar `offers.json`:
   `[{"winkel","item","product","prijs","normaal_prijs"?,"eenheid_prijs"?,"geldig_tot"?,"bron_url"}]`
   (`item` is exact de naam uit `items.yaml`, `geldig_tot` als ISO-datum).
5. `python -m bot.report offers.json` (stuurt naar Discord als `DISCORD_WEBHOOK_URL` gezet is).
6. Commit `data/prijzen.sqlite` (prijsgeschiedenis) en push.
7. Rond af met één regel: welke winkels gelukt zijn, welke niet.

## Kruidvat (geblokkeerd voor servers)
AH loopt automatisch via de app-API. Kruidvat blokkeert cloud-servers en is niet in de automatische
run. Lees het handmatig uit vanaf de eigen computer: open in Claude in Chrome / de ingebouwde browser
https://www.kruidvat.nl/acties, lees de aanbiedingen, voeg ze toe aan
`offers.json` en draai `python -m bot.report offers.json`. Folder-aggregators (folderz.nl,
folders.nl) tonen alleen folder-afbeeldingen zonder tekstprijzen, dus daar heeft het geen zin.
