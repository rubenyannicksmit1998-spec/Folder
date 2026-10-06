"""Verwerk de aanbiedingen die Claude heeft gevonden en meld ze.

Gebruik: python -m bot.report offers.json [--dry-run]

offers.json is een lijst van objecten met: winkel, item, product, prijs en optioneel
normaal_prijs, eenheid_prijs, geldig_tot, bron_url.
"""
import argparse
import json
import os

import yaml

from . import history, notify, rank
from .models import Offer


def load_offers(path: str, items: list[dict]) -> list[Offer]:
    namen = {i["naam"] for i in items}
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    offers = []
    for a in raw:
        if a.get("item") not in namen:  # alleen dingen van onze lijst
            continue
        offers.append(Offer(
            winkel=a["winkel"], item=a["item"], product=a["product"], prijs=float(a["prijs"]),
            normaal_prijs=a.get("normaal_prijs"), eenheid_prijs=a.get("eenheid_prijs"),
            geldig_tot=a.get("geldig_tot"), bron_url=a.get("bron_url"),
        ))
    return offers


def run(offers_path: str, dry_run: bool = False, items_path: str = "items.yaml",
        db_path: str | None = None) -> str:
    with open(items_path, encoding="utf-8") as f:
        items = yaml.safe_load(f)["items"]
    offers = load_offers(offers_path, items)
    db = history.connect(db_path or os.environ.get("DB_PATH", "data/prijzen.sqlite"))

    grouped = rank.filter_and_group(offers, items)
    laagste = {item: history.lowest_known(db, item) for item in grouped}
    bericht = notify.format_message(grouped, laagste)
    history.record(db, offers)

    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if dry_run or not webhook:
        print(bericht)
    else:
        notify.send_discord(webhook, bericht)
        print("Verstuurd naar Discord.")
    return bericht


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("offers")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    run(a.offers, a.dry_run)
