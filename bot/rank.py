from collections import defaultdict

from .models import Offer


def filter_and_group(offers: list[Offer], items: list[dict]) -> dict[str, list[Offer]]:
    """Pas max_prijs toe en sorteer per item van goedkoop naar duur."""
    max_prijs = {i["naam"]: i.get("max_prijs") for i in items}
    grouped: dict[str, list[Offer]] = defaultdict(list)
    for o in offers:
        limiet = max_prijs.get(o.item)
        if limiet is not None and o.prijs > limiet:
            continue
        grouped[o.item].append(o)
    return {k: sorted(v, key=lambda o: o.prijs) for k, v in grouped.items()}
