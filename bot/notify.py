import httpx

from .models import Offer

DISCORD_LIMIT = 1900


def format_message(grouped: dict[str, list[Offer]], laagste: dict[str, float | None]) -> str:
    if not grouped:
        return "Deze week geen aanbiedingen gevonden voor jullie lijst."
    regels = ["**🛒 Aanbiedingen voor jullie lijst**"]
    for item, offers in grouped.items():
        beste = offers[0]
        regels.append(f"\n**{item}**")
        for o in offers[:3]:
            korting = f" (normaal € {o.normaal_prijs:.2f})" if o.normaal_prijs else ""
            tot = f", t/m {o.geldig_tot}" if o.geldig_tot else ""
            regels.append(f"• {o.winkel}: {o.product} — **€ {o.prijs:.2f}**{korting}{tot}")
        prev = laagste.get(item)
        if prev is not None and beste.prijs < prev:
            regels.append(f"  🔥 Laagste prijs sinds we bijhouden (eerder € {prev:.2f})")
    return "\n".join(regels)


def split_message(text: str, limit: int = DISCORD_LIMIT) -> list[str]:
    parts, cur = [], ""
    for line in text.split("\n"):
        if cur and len(cur) + len(line) + 1 > limit:
            parts.append(cur)
            cur = line
        else:
            cur = f"{cur}\n{line}" if cur else line
    if cur:
        parts.append(cur)
    return parts


def send_discord(webhook_url: str, text: str) -> None:
    for part in split_message(text):
        httpx.post(webhook_url, json={"content": part}, timeout=15).raise_for_status()
