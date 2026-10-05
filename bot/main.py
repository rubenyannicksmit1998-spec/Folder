import argparse
import os
import sys

import yaml

from . import history, notify, rank
from .extract import extract_offers
from .sources import fetch_text


def load(path: str):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def run(dry_run: bool = False) -> str:
    items = load("items.yaml")["items"]
    stores = load("stores.yaml")["stores"]
    db = history.connect(os.environ.get("DB_PATH", "data/prijzen.sqlite"))

    alle = []
    for store in stores:
        for url in store["bronnen"]:
            try:
                tekst = fetch_text(url)
                alle += extract_offers(store["naam"], tekst, items, bron_url=url)
            except Exception as e:  # één kapotte bron mag de rest niet stoppen
                print(f"WAARSCHUWING {store['naam']} {url}: {e}", file=sys.stderr)

    grouped = rank.filter_and_group(alle, items)
    laagste = {item: history.lowest_known(db, item) for item in grouped}
    bericht = notify.format_message(grouped, laagste)
    history.record(db, alle)

    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if dry_run or not webhook:
        print(bericht)
    else:
        notify.send_discord(webhook, bericht)
    return bericht


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="print i.p.v. naar Discord sturen")
    run(p.parse_args().dry_run)
