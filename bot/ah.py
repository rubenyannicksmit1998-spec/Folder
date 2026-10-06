"""Albert Heijn bonus-aanbiedingen via de (onofficiële) app-API.

De AH-website blokkeert servers, de app-API niet. Per item uit items.yaml zoeken we producten
en houden we de bonus-producten over. Let op: de zoekresultaten kunnen losjes verwant zijn;
Claude beoordeelt in de run welke echt bij het item horen.

Gebruik: python -m bot.ah ah_offers.json
"""
import json
import sys

import httpx
import yaml

BASE = "https://api.ah.nl"
HEADERS = {"User-Agent": "Appie/8.22.3", "X-Application": "AHWEBSHOP", "Content-Type": "application/json"}


def get_token(client: httpx.Client) -> str:
    r = client.post(f"{BASE}/mobile-auth/v1/auth/token/anonymous", json={"clientId": "appie"})
    r.raise_for_status()
    return r.json()["access_token"]


def parse_products(item: str, products: list[dict]) -> list[dict]:
    offers = []
    for p in products:
        if not p.get("isBonus"):
            continue
        normaal = p.get("priceBeforeBonus")
        prijs = p.get("currentPrice") or normaal
        if prijs is None:
            continue
        einde = p.get("bonusEndDate")
        if not einde or einde.startswith("2999"):  # permanente "volume voordeel", geen echte aanbieding
            continue
        mech = p.get("bonusMechanism")
        offers.append({
            "winkel": "Albert Heijn",
            "item": item,
            "product": f"{p['title']} ({mech})" if mech else p["title"],
            "prijs": float(prijs),
            "normaal_prijs": float(normaal) if normaal and normaal != prijs else None,
            "eenheid_prijs": p.get("unitPriceDescription"),
            "geldig_tot": einde[:10],
            "bron_url": "https://www.ah.nl/bonus",
        })
    return offers


def fetch_bonus(items: list[dict], size: int = 20) -> list[dict]:
    out = []
    with httpx.Client(headers=HEADERS, timeout=30) as client:
        client.headers["Authorization"] = f"Bearer {get_token(client)}"
        for it in items:
            r = client.get(f"{BASE}/mobile-services/product/search/v2",
                           params={"query": it["naam"], "size": size, "sortOn": "RELEVANCE"})
            r.raise_for_status()
            out += parse_products(it["naam"], r.json().get("products", []))
    return out


if __name__ == "__main__":
    with open("items.yaml", encoding="utf-8") as f:
        items = yaml.safe_load(f)["items"]
    offers = fetch_bonus(items)
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        json.dump(offers, f, ensure_ascii=False, indent=1)
    print(f"{len(offers)} AH-bonusproducten gevonden voor {len(items)} items")
