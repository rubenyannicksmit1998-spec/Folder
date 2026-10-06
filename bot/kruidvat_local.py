"""Kruidvat-aanbiedingen uitlezen vanaf je EIGEN computer (de site blokkeert cloud-servers).

Draait lokaal: een browser haalt de pagina's op, jouw lokale Claude Code (`claude -p`, met je
eigen Claude-abonnement, geen API-key) zoekt de relevante aanbiedingen en het resultaat gaat
via bot.report naar Discord.

Vereist op je computer: Python 3.11+, `pip install -r requirements.txt`, `playwright install chromium`,
Claude Code (`claude` in je PATH, ingelogd) en de omgevingsvariabele DISCORD_WEBHOOK_URL.

Gebruik: python -m bot.kruidvat_local [--headed] [--dry-run]
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from urllib.parse import quote

import yaml

from .report import run as report_run

PROMPT = """Hieronder staat tekst van Kruidvat-pagina's (aanbiedingen/zoekresultaten) en een boodschappenlijst.
Geef ALLEEN producten die in de aanbieding/actie zijn en echt bij een item op de lijst passen.
Verzin nooit prijzen. Bij "2 voor €5" reken je om naar prijs per stuk en noem dat in 'product'.
Antwoord uitsluitend met een JSON-lijst, zonder uitleg, met objecten:
{{"winkel":"Kruidvat","item":<exacte naam uit de lijst>,"product":...,"prijs":<getal in euro>,
"normaal_prijs":<getal of null>,"geldig_tot":<YYYY-MM-DD of null>,"bron_url":<url van de pagina>}}
Is er niets, antwoord dan [].

Boodschappenlijst:
{lijst}

Pagina's:
{paginas}
"""


def extract_json_list(text: str) -> list[dict]:
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        raise ValueError(f"Geen JSON-lijst in antwoord van Claude: {text[:200]!r}")
    return json.loads(m.group(0))


def render(urls: list[str], headed: bool) -> dict[str, str]:
    from playwright.sync_api import sync_playwright

    out = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        page = browser.new_page(locale="nl-NL")
        for url in urls:
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
                if resp is not None and resp.status >= 400:
                    print(f"WAARSCHUWING {url}: HTTP {resp.status}", file=sys.stderr)
                    continue
                page.wait_for_timeout(4000)
                for _ in range(6):
                    page.mouse.wheel(0, 3000)
                    page.wait_for_timeout(500)
                out[url] = page.inner_text("body")[:40000]
            except Exception as e:
                print(f"WAARSCHUWING {url}: {e}", file=sys.stderr)
        browser.close()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--headed", action="store_true", help="zichtbare browser (minder snel geblokkeerd)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    items = yaml.safe_load(open("items.yaml", encoding="utf-8"))["items"]
    store = next(s for s in yaml.safe_load(open("stores.yaml", encoding="utf-8"))["stores"]
                 if s["naam"] == "Kruidvat")
    urls = list(store["bronnen"])
    if store.get("zoek_url"):
        urls += [store["zoek_url"].format(item=quote(i["naam"])) for i in items]

    paginas = render(urls, args.headed)
    if not paginas:
        sys.exit("Geen enkele Kruidvat-pagina kon worden opgehaald.")
    prompt = PROMPT.format(
        lijst="\n".join(f"- {i['naam']}" for i in items),
        paginas="\n\n".join(f"### {u}\n{t}" for u, t in paginas.items()),
    )
    res = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=600)
    if res.returncode != 0:
        sys.exit(f"claude -p mislukte: {res.stderr[:300]}")
    offers = extract_json_list(res.stdout)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(offers, f, ensure_ascii=False)
    report_run(f.name, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
