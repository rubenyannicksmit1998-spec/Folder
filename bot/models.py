from dataclasses import dataclass


@dataclass
class Offer:
    winkel: str
    item: str  # naam uit items.yaml waar dit bij hoort
    product: str
    prijs: float  # prijs per verpakking in euro
    normaal_prijs: float | None = None
    eenheid_prijs: str | None = None  # bv. "€ 5,98 / kg"
    geldig_tot: str | None = None  # ISO-datum
    bron_url: str | None = None
