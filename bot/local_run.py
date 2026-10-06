"""Alles-in-één run op je EIGEN computer (thuis-IP, dus geen blokkades).

Per winkel: browser haalt de pagina's op (AH via app-API), jouw lokale Claude Code (`claude -p`,
met je eigen abonnement, geen API-key) kiest de aanbiedingen die bij items.yaml passen, daarna gaat
alles via bot.report naar Discord en de prijsgeschiedenis.

Vereist: Python 3.11+, `pip install -r requirements.txt`, `playwright install chromium`,
Claude Code (`claude` in PATH, ingelogd) en DISCORD_WEBHOOK_URL (of .env.local).

Gebruik: python -m bot.local_run [--headed] [--dry-run] [--only Lidl,Aldi]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from urllib.parse import quote

import yaml

from .ah import fetch_bonus
from .report import run as report_run

PROMPT = """Hieronder staat tekst van {winkel}-pagina's (aanbiedingen/zoekresultaten) en een boodschappenlijst.
Geef ALLEEN producten die in de aanbieding/actie zijn en echt bij een item op de lijst passen
(zelfde soort product, houd rekening met de opmerking). Sla producten over die niet verkrijgbaar zijn.
Verzin nooit prijzen. Bij "2 voor 5 euro" reken je om naar prijs per stuk en noem dat in 'product'.
Antwoord uitsluitend met een JSON-lijst, zonder uitleg, met objecten:
{{"winkel":"{winkel}","item":<exacte naam uit de lijst>,"product":...,"prijs":<getal in euro>,
"normaal_prijs":<getal of null>,"geldig_tot":<YYYY-MM-DD of null>,"bron_url":<url van de pagina>}}
Is er niets, antwoord dan [].

Boodschappenlijst:
{lijst}

Pagina's:
{paginas}
"""


def load_env_local(path: str = ".env.local") -> None:
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v)


def extract_json_list(text: str) -> list[dict]:
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise ValueError(f"Geen JSON-lijst in antwoord van Claude: {text[:200]!r}")
    return json.loads(m.group(0))


def render(page, url: str) -> str | None:
    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
        if resp is not None and resp.status >= 400:
            print(f"WAARSCHUWING {url}: HTTP {resp.status}", file=sys.stderr)
            return None
        page.wait_for_timeout(4000)
        for _ in range(6):  # lazy-loaded producten
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(500)
        return page.inner_text("body")[:40000]
    except Exception as e:
        print(f"WAARSCHUWING {url}: {e}", file=sys.stderr)
        return None


def ask_claude(prompt: str) -> list[dict]:
    res = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=900)
    if res.returncode != 0:
        raise RuntimeError(f"claude -p mislukte: {res.stderr[:300]}")
    return extract_json_list(res.stdout)


def store_urls(store: dict, items: list[dict]) -> list[str]:
    urls = list(store["bronnen"])
    if store.get("zoek_url"):
        urls += [store["zoek_url"].format(item=quote(i["naam"])) for i in items]
    return urls


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--headed", action="store_true", help="zichtbare browser (minder snel geblokkeerd)")
    ap.add_argument("--dry-run", action="store_true", help="print i.p.v. naar Discord sturen")
    ap.add_argument("--only", help="alleen deze winkels, komma-gescheiden")
    args = ap.parse_args()
    load_env_local()

    items = yaml.safe_load(open("items.yaml", encoding="utf-8"))["items"]
    stores = yaml.safe_load(open("stores.yaml", encoding="utf-8"))["stores"]
    if args.only:
        wanted = {n.strip().lower() for n in args.only.split(",")}
        stores = [s for s in stores if s["naam"].lower() in wanted]
    lijst = "\n".join(f"- {i['naam']}" + (f" ({i['opmerking']})" if i.get("opmerking") else "") for i in items)

    from playwright.sync_api import sync_playwright

    alle: list[dict] = []
    mislukt: list[str] = []
    with sync_playwright() as p:
        opts = {"headless": not args.headed}
        if os.environ.get("CHROMIUM_PATH"):  # alleen nodig als Playwright zijn eigen Chromium niet vindt
            opts["executable_path"] = os.environ["CHROMIUM_PATH"]
            if os.environ.get("HTTPS_PROXY"):
                opts["proxy"] = {"server": os.environ["HTTPS_PROXY"]}
        browser = p.chromium.launch(**opts)
        page = browser.new_page(locale="nl-NL")
        for store in stores:
            naam = store["naam"]
            try:
                if store.get("api") == "ah":
                    kandidaten = fetch_bonus(items)
                    paginas = {"https://www.ah.nl/bonus": json.dumps(kandidaten, ensure_ascii=False)}
                else:
                    paginas = {u: t for u in store_urls(store, items) if (t := render(page, u))}
                if not paginas:
                    raise RuntimeError("geen enkele pagina kon worden opgehaald")
                prompt = PROMPT.format(
                    winkel=naam, lijst=lijst,
                    paginas="\n\n".join(f"### {u}\n{t}" for u, t in paginas.items()),
                )
                gevonden = ask_claude(prompt)
                print(f"{naam}: {len(gevonden)} aanbiedingen", file=sys.stderr)
                alle += gevonden
            except Exception as e:  # één kapotte winkel stopt de rest niet
                print(f"MISLUKT {naam}: {e}", file=sys.stderr)
                mislukt.append(naam)
        browser.close()

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(alle, f, ensure_ascii=False)
    report_run(f.name, dry_run=args.dry_run)
    if mislukt:
        print(f"Niet gelukt: {', '.join(mislukt)}", file=sys.stderr)


if __name__ == "__main__":
    main()
