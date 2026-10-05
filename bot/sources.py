import io

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

MAX_CHARS = 120_000
HEADERS = {"User-Agent": "Mozilla/5.0 (aanbiedingen-bot; persoonlijk gebruik)"}


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    text = soup.get_text("\n", strip=True)
    return text[:MAX_CHARS]


def pdf_to_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return text[:MAX_CHARS]


def fetch_text(url: str) -> str:
    resp = httpx.get(url, headers=HEADERS, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    if "pdf" in resp.headers.get("content-type", "") or url.lower().endswith(".pdf"):
        return pdf_to_text(resp.content)
    return html_to_text(resp.text)
