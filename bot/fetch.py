"""Haal een pagina op zoals een echte browser (JavaScript uitgevoerd) en print de tekst.

Gebruik: python -m bot.fetch URL [--max 60000]
"""
import argparse
import os
import sys

from .sources import MAX_CHARS, fetch_text

CHROMIUM = os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium")


def render_text(url: str, max_chars: int = MAX_CHARS) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        opts = {}
        if os.path.exists(CHROMIUM):
            opts["executable_path"] = CHROMIUM
        if os.environ.get("HTTPS_PROXY"):
            opts["proxy"] = {"server": os.environ["HTTPS_PROXY"]}
        browser = p.chromium.launch(**opts)
        try:
            page = browser.new_page(locale="nl-NL")
            resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
            if resp is not None and resp.status >= 400:
                raise RuntimeError(f"HTTP {resp.status} (waarschijnlijk geblokkeerd of verkeerde URL)")
            page.wait_for_timeout(4000)
            for _ in range(6):  # lazy-loaded producten
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(500)
            return page.inner_text("body")[:max_chars]
        finally:
            browser.close()


def get_text(url: str, max_chars: int = MAX_CHARS) -> str:
    if url.lower().endswith(".pdf"):
        return fetch_text(url)[:max_chars]
    return render_text(url, max_chars)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--max", type=int, default=MAX_CHARS)
    args = ap.parse_args()
    try:
        print(get_text(args.url, args.max))
    except Exception as e:
        print(f"FOUT: {e}", file=sys.stderr)
        sys.exit(1)
