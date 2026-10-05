import os

import anthropic

from .models import Offer

MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")

TOOL = {
    "name": "meld_aanbiedingen",
    "description": "Geef alle aanbiedingen uit de tekst die passen bij een item van de boodschappenlijst.",
    "input_schema": {
        "type": "object",
        "properties": {
            "aanbiedingen": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "item": {"type": "string", "description": "Exacte naam uit de boodschappenlijst"},
                        "product": {"type": "string", "description": "Productnaam zoals in de folder"},
                        "prijs": {"type": "number", "description": "Aanbiedingsprijs per verpakking in euro"},
                        "normaal_prijs": {"type": ["number", "null"]},
                        "eenheid_prijs": {"type": ["string", "null"], "description": "bv. '€ 5,98 / kg' als vermeld"},
                        "geldig_tot": {"type": ["string", "null"], "description": "ISO-datum YYYY-MM-DD als vermeld"},
                    },
                    "required": ["item", "product", "prijs"],
                },
            }
        },
        "required": ["aanbiedingen"],
    },
}

SYSTEM = (
    "Je leest tekst van een supermarktfolder of aanbiedingenpagina. "
    "Je krijgt een boodschappenlijst. Geef ALLEEN aanbiedingen terug die echt bij een item op de lijst passen "
    "(zelfde soort product). Verzin nooit prijzen; als een prijs onduidelijk is, laat het product weg. "
    "Bij multi-buy ('2 voor €5') reken je om naar de prijs per stuk en noem je dat in 'product'."
)


def extract_offers(winkel: str, page_text: str, items: list[dict], bron_url: str | None = None,
                   client: anthropic.Anthropic | None = None) -> list[Offer]:
    client = client or anthropic.Anthropic()
    lijst = "\n".join(
        f"- {i['naam']}" + (f" ({i['opmerking']})" if i.get("opmerking") else "") for i in items
    )
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM,
        tools=[TOOL],
        tool_choice={"type": "tool", "name": TOOL["name"]},
        messages=[{
            "role": "user",
            "content": f"Winkel: {winkel}\n\nBoodschappenlijst:\n{lijst}\n\nFoldertekst:\n{page_text}",
        }],
    )
    namen = {i["naam"] for i in items}
    offers: list[Offer] = []
    for block in msg.content:
        if block.type != "tool_use":
            continue
        for a in block.input.get("aanbiedingen", []):
            if a.get("item") not in namen:
                continue
            offers.append(Offer(
                winkel=winkel, item=a["item"], product=a["product"], prijs=float(a["prijs"]),
                normaal_prijs=a.get("normaal_prijs"), eenheid_prijs=a.get("eenheid_prijs"),
                geldig_tot=a.get("geldig_tot"), bron_url=bron_url,
            ))
    return offers
