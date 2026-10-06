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


def test_report_end_to_end(tmp_path, monkeypatch, capsys):
    import json
    from bot import report

    (tmp_path / "items.yaml").write_text("items:\n  - naam: Melk\n  - naam: Luiers\n    max_prijs: 5\n")
    offers = tmp_path / "offers.json"
    offers.write_text(json.dumps([
        {"winkel": "Jumbo", "item": "Melk", "product": "Jumbo melk", "prijs": 1.1},
        {"winkel": "Aldi", "item": "Melk", "product": "Aldi melk", "prijs": 0.99},
        {"winkel": "Aldi", "item": "Luiers", "product": "Duur", "prijs": 9},
        {"winkel": "Aldi", "item": "Onbekend", "product": "x", "prijs": 1},
    ]))
    monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    msg = report.run(str(offers), items_path=str(tmp_path / "items.yaml"), db_path=str(tmp_path / "p.db"))
    assert msg.index("Aldi") < msg.index("Jumbo")  # goedkoopste eerst
    assert "Duur" not in msg and "Onbekend" not in msg
    # tweede run met lagere prijs -> record
    offers.write_text(json.dumps([{"winkel": "Aldi", "item": "Melk", "product": "Aldi melk", "prijs": 0.8}]))
    assert "Laagste prijs" in report.run(str(offers), items_path=str(tmp_path / "items.yaml"),
                                         db_path=str(tmp_path / "p.db"))


def test_discord_post(httpx_mock=None):
    import json
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from bot.notify import send_discord

    got = []

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            got.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
            self.send_response(204)
            self.end_headers()

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.handle_request, daemon=True).start()
    send_discord(f"http://127.0.0.1:{srv.server_port}/hook", "hallo")
    assert got == [{"content": "hallo"}]


def test_ah_parse_products():
    from bot.ah import parse_products

    prods = [
        {"title": "Calvé pot", "isBonus": False, "priceBeforeBonus": 4.75},
        {"title": "AH pindakaas", "isBonus": True, "priceBeforeBonus": 7.38, "currentPrice": 7.16,
         "bonusMechanism": "3% volume voordeel", "bonusEndDate": "2999-12-31"},
        {"title": "Becel", "isBonus": True, "priceBeforeBonus": 3.0, "bonusMechanism": "1+1 gratis",
         "bonusEndDate": "2026-10-12"},
    ]
    o = parse_products("Pindakaas", prods)
    assert [x["product"] for x in o] == ["Becel (1+1 gratis)"]  # permanente korting valt af
    assert o[0]["prijs"] == 3.0 and o[0]["normaal_prijs"] is None and o[0]["geldig_tot"] == "2026-10-12"
