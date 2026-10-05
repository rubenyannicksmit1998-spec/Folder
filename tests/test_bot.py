from bot.models import Offer
from bot.notify import format_message, split_message
from bot.rank import filter_and_group
from bot.sources import html_to_text


def test_html_to_text_strips_scripts():
    assert html_to_text("<script>x()</script><p>Pindakaas € 1,99</p>") == "Pindakaas € 1,99"


def test_rank_applies_max_prijs_and_sorts():
    items = [{"naam": "Luiers", "max_prijs": 8.0}, {"naam": "Melk"}]
    offers = [
        Offer("AH", "Luiers", "Pampers", 9.5),
        Offer("Lidl", "Luiers", "Lupilu", 6.0),
        Offer("Jumbo", "Melk", "Jumbo melk", 1.2),
        Offer("AH", "Melk", "AH melk", 1.0),
    ]
    g = filter_and_group(offers, items)
    assert [o.winkel for o in g["Luiers"]] == ["Lidl"]
    assert [o.winkel for o in g["Melk"]] == ["AH", "Jumbo"]


def test_message_flags_record_low():
    g = {"Melk": [Offer("AH", "Melk", "AH melk", 1.0)]}
    assert "Laagste prijs" in format_message(g, {"Melk": 1.2})
    assert "Laagste prijs" not in format_message(g, {"Melk": 0.9})


def test_split_message_respects_limit():
    text = "\n".join(["x" * 100] * 50)
    assert all(len(p) <= 1900 for p in split_message(text))
