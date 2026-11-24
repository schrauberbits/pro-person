#!/usr/bin/env python3
"""Baut index.html, die Antwortseiten, sitemap.xml und robots.txt aus einer Datenquelle.
Aufruf im Repository-Ordner:  python3 _werkzeug/bau.py
Alle Mengen sind Richtwerte mit Quelle (Stand 24.11.2026)."""
import json, html, math, pathlib, datetime

WURZEL = pathlib.Path(__file__).resolve().parent.parent
WZ = WURZEL / "_werkzeug"
BASIS = "https://schrauberbits.github.io/pro-person/"
STAND = "2026-11-24"
INDEXNOW_KEY = "45503adea8b35baf504b2cd08281a72b"

Q_MLR = "Portionsplaner des Ministeriums für Ernährung, Ländlichen Raum und Verbraucherschutz Baden-Württemberg (2026)"
QUELLEN = {
    "mlr": ("Portionsplaner, MLR Baden-Württemberg (2026)", "https://mlr.baden-wuerttemberg.de/fileadmin/redaktion/m-mlr/intern/dateien/PDFs/Essen_und_Trinken/2026_02_Portionsplaner.pdf"),
    "vz": ("Verbraucherzentrale: Weihnachtsessen – Reste vermeiden (Stand 22.12.2025)", "https://www.verbraucherzentrale.de/wissen/lebensmittel/auswaehlen-zubereiten-aufbewahren/weihnachtsessen-reste-vermeiden-und-sinnvoll-verwerten-11231"),
    "utopia_reis": ("Utopia: Reis kochen", "https://utopia.de/ratgeber/reis-kochen-so-gelingt-dein-reis-perfekt/"),
    "rewe_basmati": ("REWE-Lexikon: Basmatireis", "https://www.rewe.de/lexikon/basmatireis/"),
    "dm_reis": ("dm: Reis", "https://www.dm.de/tipps-und-trends/food/reis-2377114"),
    "rewe_couscous": ("REWE-Lexikon: Couscous", "https://www.rewe.de/lexikon/couscous/"),
    "rewe_couscoussalat": ("REWE: Couscous-Salate (60 g pro Person)", "https://www.rewe.de/rezeptsammlung/couscous-salate/"),
    "familienkost": ("Familienkost: Couscous zubereiten (1:1)", "https://familienkost.de/rezept_couscous-zubereiten.pdf"),
    "utopia_bulgur": ("Utopia: Bulgur kochen", "https://utopia.de/ratgeber/bulgur-kochen-so-kannst-du-den-weizengries-zubereiten/"),
    "drk": ("DRK-Verpflegungsdienst: Lebensmittel-Berechnung pro Person", "https://www.bildungsinstitut-rlp.drk.de/fileadmin/downloads/Bereitschaften/Fachdienstausbildung_Verpflegungsdienst/Hintergrundinfos/02_Lebensmittel-Berechnung_pro_Person__Inforama.pdf"),
    "kurier": ("Berliner Kurier: Wie viel Grillfleisch pro Person?", "https://www.berliner-kurier.de/article/wie-viel-grillfleisch-pro-person-die-einfache-faustregel-10032461"),
    "fuersie": ("Für Sie: Wie viel Fleisch pro Person beim Grillen", "https://www.fuersie.de/grillen/wie-viel-fleisch-pro-person-beim-grillen-13044.html"),
    "lecker": ("lecker.de: Geburtstagskuchen (2 Stück je Gast)", "https://www.lecker.de/geburtstagskuchen-backrezepte-fuer-den-grossen-tag-51380.html"),
    "kuechenfibel": ("Küchenfibel: Wie viel Kuchen pro Gast", "https://www.kuechenfibel.de/faq/wie-viel-kuchen-pro-gast"),
    "getraenk": ("Getränke-Faustregel 0,5 l je Person und Stunde (rechner-portal.de, dort der Verbraucherzentrale zugeschrieben)", "https://rechner-portal.de/feste-feiern/mengen-pro-gast/getraenkemengen-rechner"),
    "dge": ("DGE-Referenzwerte Energie: Kinder 4–6 Jahre rund 1.000–1.100 kcal/Tag (Ernährungs-Umschau 3/2008)", "https://www.ernaehrungs-umschau.de/fileadmin/Ernaehrungs-Umschau/pdfs/pdf_2008/03_08/EU03_168_177.qxd.pdf"),
}

SORTEN = {
    "basmati": dict(name="Basmati- oder Jasminreis", kurz="Reis", roh=True, b=70, h=100, wasserJeG=1.9,
        wasserRegel="1 Tasse Reis auf 1,5 Tassen Wasser (Quellmethode)",
        zeit="10–12 Min. mit Deckel bei kleiner Hitze köcheln, dann kurz ziehen lassen", packung=500, packungText="übliche Packung",
        quelle="Portionsplaner MLR Baden-Württemberg 2026 (Reis 60–80 g Beilage, 80–100 g Hauptgericht); Wasser 1:1,5 nach Utopia; Garzeit nach REWE-Warenkunde",
        qk=["mlr", "utopia_reis", "rewe_basmati"]),
    "langkorn": dict(name="Langkornreis oder Parboiled-Reis", kurz="Reis", roh=True, b=70, h=100, wasserJeG=2.5,
        wasserRegel="1 Tasse Reis auf 2 Tassen Wasser (Quellmethode)",
        zeit="laut Packung, meist 15–20 Min. mit Deckel quellen lassen", packung=500, packungText="übliche Packung",
        quelle="Portionsplaner MLR Baden-Württemberg 2026; Wasser 1:2 nach dm", qk=["mlr", "dm_reis"]),
    "naturreis": dict(name="Naturreis (Vollkornreis)", kurz="Naturreis", roh=True, b=70, h=100, wasserJeG=2.5,
        wasserRegel="1 Tasse Reis auf 2 Tassen Wasser, lieber etwas mehr",
        zeit="laut Packung, meist 30–40 Min.", packung=500, packungText="übliche Packung",
        quelle="Portionsplaner MLR Baden-Württemberg 2026; Wasser 1:2 nach Utopia", qk=["mlr", "utopia_reis"]),
    "nudeln": dict(name="Nudeln (trocken)", kurz="Nudeln", roh=True, b=70, h=110, wasserJeG=10,
        wasserRegel="1 Liter Wasser je 100 g Nudeln, danach abgießen",
        zeit="laut Packung, meist 8–12 Min.", packung=500, packungText="übliche Packung",
        quelle="Portionsplaner MLR Baden-Württemberg 2026 (Nudeln 60–80 g Beilage, 100–120 g Hauptgericht)", qk=["mlr"]),
    "kartoffeln": dict(name="Kartoffeln", kurz="Kartoffeln", roh=False, b=190, h=275, wasserJeG=0,
        wasserRegel="knapp mit Wasser bedecken",
        zeit="je nach Größe etwa 20–25 Min. (Gabelprobe)", packung=2500, packungText="übliches Netz",
        quelle="Portionsplaner MLR Baden-Württemberg 2026 (Kartoffeln roh, ungeschält: 175–200 g Beilage, 250–300 g Hauptgericht)", qk=["mlr"]),
    "couscous": dict(name="Couscous", kurz="Couscous", roh=True, b=60, h=90, wasserJeG=1,
        wasserRegel="gleiche Menge kochendes Wasser oder Brühe (1:1), je nach Packung bis 1:1,5",
        zeit="5–10 Min. zugedeckt quellen lassen, mit der Gabel auflockern", packung=500, packungText="übliche Packung",
        quelle="REWE (60 g pro Person, 1:1, etwa 10 Min.), Familienkost (1:1); Hauptgericht 90 g als 1,5-fache Beilage (eigener Richtwert, wie bei Bulgur 50/80 g)",
        qk=["rewe_couscoussalat", "rewe_couscous", "familienkost"]),
    "bulgur_fein": dict(name="Bulgur fein oder Schnellbulgur", kurz="Bulgur", roh=True, b=50, h=80, wasserJeG=1,
        wasserRegel="1:1 mit heißem Wasser übergießen",
        zeit="einige Minuten zugedeckt quellen lassen", packung=500, packungText="übliche Packung",
        quelle="Utopia (50 g Beilage, 80 g Hauptgericht, Schnellbulgur 1:1)", qk=["utopia_bulgur"]),
    "bulgur_grob": dict(name="Bulgur grob", kurz="Bulgur", roh=True, b=50, h=80, wasserJeG=2,
        wasserRegel="1:2 mit kochendem Wasser übergießen (200 g auf 400 ml)",
        zeit="15 Min. abgedeckt quellen lassen", packung=500, packungText="übliche Packung",
        quelle="Utopia (50 g Beilage, 80 g Hauptgericht, grob 1:2, 15 Min.)", qk=["utopia_bulgur"]),
}

GETRAENK_HINWEIS = "0,5 l je Erwachsenem und Stunde, Kinder 0,4 l; mindestens die Hälfte Wasser und Alkoholfreies"
FEIER = {
    "buffet": dict(name="Buffet", posten=[
        dict(name="Fleisch und Fisch", jeP=125, einheit="g", hinweis="75 g Fleisch + 50 g Fisch je Person"),
        dict(name="Salate (Nudel-, Kartoffel-, Blattsalat)", jeP=250, einheit="g", hinweis="alle Salate zusammen"),
        dict(name="Brot oder Brötchen", jeP=2, einheit="stueck", stueckEins="Scheibe/Brötchen", stueckViele="Scheiben/Brötchen", hinweis="2 je Person"),
        dict(name="Nachtisch", jeP=125, einheit="g", hinweis="100–150 g je Person"),
        dict(name="Getränke", typ="getraenk", einheit="l", hinweis=GETRAENK_HINWEIS)],
        notiz="Die Verbraucherzentrale rechnet beim Büfett mit insgesamt etwa 800 g Essen je Person; je größer die Auswahl, desto kleiner die einzelnen Mengen.",
        quelle="Verbraucherzentrale (Stand 12/2025), Portionsplaner MLR Baden-Württemberg 2026, DRK-Verpflegungsdienst, Getränke-Faustregel"),
    "grill": dict(name="Grillabend", posten=[
        dict(name="Grillgut (Fleisch, Würstchen)", jeP=325, einheit="g", hinweis="300–350 g je Person; mit Grillkäse oder -gemüse weniger"),
        dict(name="Salate", jeP=250, einheit="g", hinweis="alle Salate zusammen"),
        dict(name="Brot oder Baguette", jeP=4, einheit="stueck", stueckEins="Scheibe", stueckViele="Scheiben", hinweis="4–5 Scheiben je Person"),
        dict(name="Gemüse und Rohkost", jeP=100, einheit="g", hinweis="etwa 100 g je Person"),
        dict(name="Getränke", typ="getraenk", einheit="l", hinweis=GETRAENK_HINWEIS)],
        notiz="Gibt es keine Salate, doppelt so viel Brot rechnen.",
        quelle="Berliner Kurier (Grillgut 300–350 g), Für Sie (Salate 250 g, Brot 4–5 Scheiben, Gemüse 100 g), Getränke-Faustregel"),
    "kaffee": dict(name="Kaffee und Kuchen", posten=[
        dict(name="Kuchen", jeP=2, einheit="stueck", stueckEins="Stück", stueckViele="Stück", kuchen=True, hinweis="2 Stück je Gast"),
        dict(name="Kaffee oder Tee", jeP=0.3, kinderJeP=0, einheit="l", hinweis="etwa 2 Tassen je Erwachsenem"),
        dict(name="Wasser, Saft, Limo", typ="getraenkOhneKaffee", einheit="l", hinweis="Getränke insgesamt 0,5 l je Erwachsenem und Stunde (Kinder 0,4 l), abzüglich Kaffee")],
        notiz="Bei einem großen Kuchenbuffet mit vielen Sorten reicht oft 1 Stück je Gast; gibt es nur Kuchen, eher 2–3.",
        quelle="lecker.de (2 Stück je Gast), Küchenfibel (Springform 12, Blech 20 Stück), DRK-Verpflegungsdienst (Kaffee/Tee 2–3 dl), Getränke-Faustregel"),
    "fingerfood": dict(name="Fingerfood", posten=[
        dict(name="Häppchen", jeP=13, einheit="stueck", stueckEins="Häppchen", stueckViele="Häppchen", hinweis="12–15 je Person, wenn es sonst nichts gibt"),
        dict(name="Getränke", typ="getraenk", einheit="l", hinweis=GETRAENK_HINWEIS)],
        notiz="Als Vorspeise vor einem Essen reichen 8–10 Häppchen je Person.",
        quelle="Verbraucherzentrale (12–15 Häppchen), DRK-Verpflegungsdienst (Apéro 8–10), Getränke-Faustregel"),
}
D = dict(sorten={k: {x: y for x, y in v.items() if x != "qk"} for k, v in SORTEN.items()},
         feier=FEIER, kinderFaktor=0.5, hunger={"wenig": 0.8, "normal": 1, "viel": 1.25},
         getraenk={"erwachsene": 0.5, "kinder": 0.4}, kuchen={"blech": 20, "rund": 12})

# ---------- Hilfen ----------
def de(n, d=0):
    s = f"{n:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s
def gramm(g):
    if g < 1000: return f"{de(round(g/5)*5)} g"
    kg = round(g/50)*50/1000
    s = de(kg, 2 if g < 10000 else 1).rstrip("0").rstrip(",")
    return f"{s} kg"
def ml(m):
    if m < 1000: return f"{de(round(m/10)*10)} ml"
    return de(round(m/100)*100/1000, 1).replace(",0", "") + " l"
E = html.escape

# ---------- Antwortseiten ----------
PERSONEN = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50]
SEITEN = []  # (slug, frage)

def tabelle_sorte(sid):
    s = SORTEN[sid]
    zeilen = []
    for p in PERSONEN:
        wb = f"{ml(p*s['b']*s['wasserJeG'])}" if s["wasserJeG"] else "–"
        zeilen.append(f"<tr><td>{p} {'Person' if p == 1 else 'Personen'}</td><td class=r>{gramm(p*s['b'])}</td><td class=r>{gramm(p*s['h'])}</td>" + (f"<td class=r>{wb}</td>" if s["wasserJeG"] else "") + "</tr>")
    kopf = "<tr><th>Personen</th><th class=r>Beilage</th><th class=r>Hauptgericht</th>" + ("<th class=r>Wasser (Beilage)</th>" if s["wasserJeG"] else "") + "</tr>"
    return f"<table><thead>{kopf}</thead><tbody>{''.join(zeilen)}</tbody></table>"

def quellen_html(keys):
    return "<ul class=quellen>" + "".join(f'<li><a href="{E(QUELLEN[k][1])}" rel="nofollow noopener">{E(QUELLEN[k][0])}</a></li>' for k in keys) + "</ul>"

def seite(slug, frage, titel, beschreibung, antwort_html, body_html, rechner_hash, quellen, faq_antwort):
    SEITEN.append((slug, frage))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": frage, "acceptedAnswer": {"@type": "Answer", "text": faq_antwort}}]}
    return slug, f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(titel)}</title>
<meta name="description" content="{E(beschreibung)}">
<link rel="canonical" href="{BASIS}{slug}/">
<style>{STIL}</style>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script data-goatcounter="https://schrauberbits.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</head>
<body>
<div class="wrap">
<div class="top"><a class="brand" href="../">🍚 Mengen pro Person</a></div>
<h1>{E(frage)}</h1>
<div class="answer">{antwort_html}</div>
{body_html}
<div class="actions"><a class="btn" href="../?ref=seite-{slug}{rechner_hash}">Mit eigenen Werten rechnen und als Liste teilen</a></div>
<h2>Quellen</h2>
<p class="hint">Richtwerte ohne Gewähr; die Packungsangabe geht vor. Keine Ernährungsberatung.</p>
{quellen_html(quellen)}
<section class="mehr"><h2>Weitere Fragen</h2><ul class="links">{{LINKS:{slug}}}</ul></section>
<footer>Stand: 24.11.2026 · Kostenlos, ohne Anmeldung, ohne Werbung – ein Hobbyprojekt, mit KI-Hilfe erstellt. Aufrufe werden anonym und ohne Cookies gezählt (GoatCounter).<br><a href="../">Mengen-Rechner mit Mitbringliste</a></footer>
</div>
</body>
</html>
"""

def sorte_seite(sid, slug, frage, extra_html="", extra_q=None):
    s = SORTEN[sid]
    kurz = s["kurz"]
    roh = "roh" if s["roh"] else "roh, ungeschält"
    antwort = (f"<p class=gross>{s['b']} g {E(kurz)} ({roh}) als Beilage, {s['h']} g als Hauptgericht – je Erwachsenem.</p>"
               f"<p>Für 4 Personen also {gramm(4*s['b'])} als Beilage oder {gramm(4*s['h'])} als Hauptgericht. Kinder bis etwa 10 Jahre essen ungefähr die Hälfte.</p>"
               + (f"<p><b>Wasser:</b> {E(s['wasserRegel'])}" + (f" – für 4 Portionen Beilage etwa {ml(4*s['b']*s['wasserJeG'])}" if s['wasserJeG'] else "") + f". <b>Garzeit:</b> {E(s['zeit'])}.</p>"))
    body = f"<h2>Tabelle: {E(kurz)} für 1 bis 50 Personen</h2>" + tabelle_sorte(sid) + extra_html
    faq = f"{s['b']} g {kurz} ({roh}) je Person als Beilage, {s['h']} g als Hauptgericht. Wasser: {s['wasserRegel']}. Garzeit: {s['zeit']}."
    return seite(slug, frage, f"{frage} {s['b']} g Beilage, {s['h']} g Hauptgericht – Tabelle bis 50 Personen",
                 f"{frage} {s['b']} g {kurz} {roh} als Beilage, {s['h']} g als Hauptgericht. Mit Wasser, Garzeit und Tabelle für 1 bis 50 Personen.",
                 antwort, body, f"#beilage?sorte={sid}&art=beilage&p=4", extra_q or s_qk(sid), faq)

def s_qk(sid): return SORTEN[sid]["qk"]

def wasser_seite():
    zeilen = "".join(f"<tr><td>{E(SORTEN[k]['name'])}</td><td>{E(SORTEN[k]['wasserRegel'])}</td><td>{E(SORTEN[k]['zeit'])}</td></tr>" for k in ["basmati", "langkorn", "naturreis"])
    mengen = "".join(f"<tr><td>{g} g Reis</td><td class=r>{ml(g*1.9)}</td><td class=r>{ml(g*2.5)}</td></tr>" for g in [70, 100, 140, 200, 250, 280, 350, 500, 1000])
    antwort = ("<p class=gross>Basmati und Jasmin: 1 Tasse Reis auf 1,5 Tassen Wasser. Langkorn-, Parboiled- und Naturreis: 1 Tasse auf 2 Tassen.</p>"
               "<p>Das gilt für die Quellmethode (Reis nimmt das ganze Wasser auf). Bei der Nudelmethode kocht der Reis in viel Wasser, das danach abgegossen wird – dann ist das Verhältnis egal. Wer nach Gewicht kocht: 280 g Reis (4 Portionen Beilage) brauchen bei Basmati etwa 530 ml, bei Langkornreis etwa 700 ml Wasser.</p>")
    body = (f"<h2>Wasser und Garzeit je Sorte</h2><table><thead><tr><th>Sorte</th><th>Wasser</th><th>Garzeit</th></tr></thead><tbody>{zeilen}</tbody></table>"
            f"<h2>Wasser nach Gewicht</h2><p class=hint>Umgerechnet mit etwa 0,8 g je ml trockenem Reis (Näherung).</p><table><thead><tr><th>Reis</th><th class=r>Basmati/Jasmin</th><th class=r>Langkorn/Natur</th></tr></thead><tbody>{mengen}</tbody></table>")
    return seite("reis-wasser-verhaeltnis", "Wie viel Wasser für Reis? Das Verhältnis Reis zu Wasser",
                 "Reis-Wasser-Verhältnis: 1:1,5 für Basmati, 1:2 für Langkornreis – mit Tabelle in ml",
                 "Verhältnis Reis zu Wasser: Basmati und Jasmin 1 Tasse auf 1,5 Tassen, Langkorn-, Parboiled- und Naturreis 1 auf 2. Mit Garzeit und Tabelle in ml nach Gewicht.",
                 antwort, body, "#beilage?sorte=basmati&art=beilage&p=4", ["utopia_reis", "dm_reis", "rewe_basmati"],
                 "Basmati und Jasmin: 1 Tasse Reis auf 1,5 Tassen Wasser; Langkorn-, Parboiled- und Naturreis: 1 Tasse auf 2 Tassen (Quellmethode).")

def gaeste_tabelle(anlass, gaeste, stunden):
    a = FEIER[anlass]
    kopf = "<tr><th>Gäste</th>" + "".join(f"<th class=r>{E(p['name'])}</th>" for p in a["posten"]) + "</tr>"
    zeilen = []
    for g in gaeste:
        zellen = []
        for p in a["posten"]:
            t = p.get("typ")
            if t == "getraenk": m = g*0.5*stunden; zellen.append(de(math.ceil(m*2)/2, 1).replace(",0", "") + " l")
            elif t == "getraenkOhneKaffee": m = g*(0.5*stunden-0.3); zellen.append(de(math.ceil(m*2)/2, 1).replace(",0", "") + " l")
            elif p["einheit"] == "g": zellen.append(gramm(g*p["jeP"]))
            elif p["einheit"] == "l": zellen.append(de(math.ceil(g*p["jeP"]*2)/2, 1).replace(",0", "") + " l")
            else:
                n = math.ceil(g*p["jeP"])
                zellen.append(f"{de(n)}" + (f" ≈ {math.ceil(n/20)} Bleche / {math.ceil(n/12)} runde" if p.get("kuchen") else ""))
        zeilen.append(f"<tr><td>{g}</td>" + "".join(f"<td class=r>{z}</td>" for z in zellen) + "</tr>")
    return f"<div class=scroll><table><thead>{kopf}</thead><tbody>{''.join(zeilen)}</tbody></table></div>"

def buffet_seite():
    antwort = ("<p class=gross>Beim Buffet rechnet man mit etwa 800 g Essen je Person (Verbraucherzentrale).</p>"
               "<p>Davon je Person etwa 75 g Fleisch und 50 g Fisch, 250 g Salate zusammen, 2 Scheiben Brot oder Brötchen und 100–150 g Nachtisch. Je mehr Auswahl, desto kleiner die einzelnen Mengen. Kinder bis etwa 10 Jahre zählen halb. Getränke: rund 0,5 l je Person und Stunde.</p>")
    body = "<h2>Tabelle: Buffet für 10 bis 60 Gäste (4 Stunden)</h2>" + gaeste_tabelle("buffet", [10, 15, 20, 25, 30, 40, 50, 60], 4)
    return seite("buffet-pro-person", "Wie viel Essen pro Person beim Buffet?",
                 "Buffet: wie viel Essen pro Person? 800 g je Gast – Tabelle für 10 bis 60 Gäste",
                 "Buffet planen: etwa 800 g Essen je Person, 125 g Fleisch und Fisch, 250 g Salate, 2 Scheiben Brot, Nachtisch und Getränke – mit Tabelle für 10 bis 60 Gäste und Mitbringliste.",
                 antwort, body, "#feier?anlass=buffet&g=20&h=4", ["vz", "mlr", "drk", "getraenk"],
                 "Etwa 800 g Essen je Person: rund 125 g Fleisch und Fisch, 250 g Salate, 2 Scheiben Brot, 100–150 g Nachtisch; Getränke etwa 0,5 l je Person und Stunde.")

def kuchen_seite():
    antwort = ("<p class=gross>2 Stück Kuchen je Gast. Ein Blechkuchen ergibt etwa 20 Stück, ein runder Kuchen (26–28 cm) etwa 12.</p>"
               "<p>Für 20 Gäste also 40 Stück: 2 Blechkuchen oder 4 runde Kuchen. Gibt es ein großes Kuchenbuffet mit vielen Sorten, reicht oft 1 Stück je Gast; gibt es nur Kuchen und sonst nichts, eher 2–3.</p>")
    body = "<h2>Tabelle: Kuchen und Kaffee für 5 bis 60 Gäste (3 Stunden)</h2>" + gaeste_tabelle("kaffee", [5, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60], 3)
    return seite("kuchen-pro-person", "Wie viel Kuchen pro Person zum Geburtstag?",
                 "Wie viel Kuchen pro Person? 2 Stück je Gast – wie viele Kuchen für 10, 20, 50 Gäste",
                 "Kuchen pro Person: 2 Stück je Gast, ein Blech ergibt etwa 20, ein runder Kuchen etwa 12 Stück. Tabelle für 5 bis 60 Gäste mit Kaffee und Getränken.",
                 antwort, body, "#feier?anlass=kaffee&g=20&h=3", ["lecker", "kuechenfibel", "drk", "getraenk"],
                 "2 Stück Kuchen je Gast; ein Blechkuchen ergibt etwa 20 Stück, ein runder Kuchen etwa 12. Für 20 Gäste: 2 Bleche oder 4 runde Kuchen.")

def party20_seite():
    antwort = ("<p class=gross>Für 20 Gäste am Buffet: etwa 16 kg Essen insgesamt – davon 2,5 kg Fleisch und Fisch, 5 kg Salate, 40 Scheiben Brot, 2,5 kg Nachtisch – und rund 40 l Getränke für 4 Stunden.</p>"
               "<p>Beim Grillabend statt Buffet: 6,5 kg Grillgut, 5 kg Salate, 80 Scheiben Brot, 2 kg Gemüse. Bei Kaffee und Kuchen: 40 Stück Kuchen (2 Bleche) und 6 l Kaffee. Kinder bis etwa 10 Jahre zählen beim Essen halb.</p>")
    body = ("<h2>Buffet</h2>" + gaeste_tabelle("buffet", [20], 4) + "<h2>Grillabend</h2>" + gaeste_tabelle("grill", [20], 4)
            + "<h2>Kaffee und Kuchen</h2>" + gaeste_tabelle("kaffee", [20], 3) + "<h2>Fingerfood</h2>" + gaeste_tabelle("fingerfood", [20], 3)
            + "<p class=hint>Tipp: Im Rechner „Alles in die Liste“ tippen und den Link an die Gäste schicken – jeder trägt ein, was er mitbringt.</p>")
    return seite("party-fuer-20-personen", "Party für 20 Personen: Wie viel Essen und Trinken?",
                 "Party für 20 Personen: wie viel Essen und Getränke? Buffet, Grillen, Kuchen – mit Mitbringliste",
                 "Mengen für 20 Gäste: Buffet (16 kg Essen, 40 l Getränke für 4 Stunden), Grillabend (6,5 kg Grillgut), Kaffee und Kuchen (40 Stück) – als Einkaufs- und Mitbringliste zum Teilen.",
                 antwort, body, "#feier?anlass=buffet&g=20&h=4", ["vz", "mlr", "kurier", "fuersie", "lecker", "kuechenfibel", "drk", "getraenk"],
                 "Für 20 Gäste am Buffet etwa 16 kg Essen (2,5 kg Fleisch und Fisch, 5 kg Salate, 40 Scheiben Brot, 2,5 kg Nachtisch) und rund 40 l Getränke für 4 Stunden.")

STIL = (WZ / "stil.css").read_text(encoding="utf-8") + ".gross{font-size:1.25rem;font-weight:700;line-height:1.3;margin:0 0 8px}.answer p{margin:0 0 8px}.answer p:last-child{margin:0}.scroll{overflow-x:auto}.quellen{font-size:.88rem;padding-left:20px}.klein{font-size:.85rem;color:var(--muted)}"
STIL = " ".join(STIL.split())

def bauen():
    seiten = [
        sorte_seite("basmati", "reis-pro-person", "Wie viel Reis pro Person?",
                    "<p class=hint>Langkorn-, Parboiled- und Naturreis: dieselben Mengen, aber mehr Wasser (1 Tasse Reis auf 2 Tassen). Siehe <a href=\"../reis-wasser-verhaeltnis/\">Verhältnis Reis zu Wasser</a>.</p>"),
        wasser_seite(),
        sorte_seite("couscous", "couscous-pro-person", "Wie viel Couscous pro Person?",
                    "<p class=hint>Für Couscous-Salat reichen meist 60 g je Person, weil Gemüse, Kräuter und Dressing dazukommen; als Hauptgericht mit wenig Beilagen eher mehr.</p>"),
        sorte_seite("kartoffeln", "kartoffeln-pro-person", "Wie viele Kartoffeln pro Person?",
                    "<p class=hint>Für Püree oder Kartoffelsalat als Hauptbeilage eher die größere Menge nehmen. 1 kg Kartoffeln reicht als Beilage für etwa 5 Personen.</p>"),
        sorte_seite("nudeln", "nudeln-pro-person", "Wie viel Nudeln pro Person?",
                    "<p class=hint>Eine 500-g-Packung reicht als Hauptgericht für etwa 4–5 Personen, als Beilage für etwa 7. Für Nudelsalat reichen 60–70 g je Person.</p>"),
        sorte_seite("bulgur_fein", "bulgur-pro-person", "Wie viel Bulgur pro Person?",
                    "<p class=hint>Grober Bulgur braucht doppelt so viel Wasser (1:2) und etwa 15 Minuten.</p>"),
        buffet_seite(), kuchen_seite(), party20_seite(),
    ]
    # Links zwischen den Seiten
    for slug, inhalt in seiten:
        links = "".join(f'<li><a href="../{s}/">{E(f)}</a></li>' for s, f in SEITEN if s != slug)
        inhalt = inhalt.replace("{LINKS:" + slug + "}", links)
        (WURZEL / slug).mkdir(exist_ok=True)
        (WURZEL / slug / "index.html").write_text(inhalt, encoding="utf-8")
    # Startseite
    v = (WZ / "index.vorlage.html").read_text(encoding="utf-8")
    schnell = []
    for sid in ["basmati", "nudeln", "kartoffeln", "couscous", "bulgur_fein"]:
        s = SORTEN[sid]
        name = {"basmati": "Reis", "bulgur_fein": "Bulgur"}.get(sid, s["kurz"])
        w = {"basmati": "1 : 1,5 (Tasse)", "nudeln": "1 l je 100 g", "kartoffeln": "bedecken", "couscous": "1 : 1", "bulgur_fein": "1 : 1"}[sid]
        schnell.append(f"      <tr><td><b>{name}</b></td><td>{s['b']} g</td><td>{s['h']} g</td><td>{w}</td></tr>")
    v = v.replace("/*SCHNELLTABELLE*/", "\n".join(schnell))
    v = v.replace("/*SEITENLINKS*/", "\n".join(f'      <li><a href="{s}/">{E(f)}</a></li>' for s, f in SEITEN))
    v = v.replace("/*STIL*/", (WZ / "stil.css").read_text(encoding="utf-8"))
    v = v.replace("/*DATEN*/", "const D=" + json.dumps(D, ensure_ascii=False) + ";")
    v = v.replace("/*SKRIPT*/", (WZ / "skript.js").read_text(encoding="utf-8"))
    (WURZEL / "index.html").write_text(v, encoding="utf-8")
    # Sitemap, robots, IndexNow-Schlüsseldatei
    urls = [BASIS] + [f"{BASIS}{s}/" for s, _ in SEITEN]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>{STAND}</lastmod></url>\n" for u in urls) + "</urlset>\n"
    (WURZEL / "sitemap.xml").write_text(sm, encoding="utf-8")
    (WURZEL / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASIS}sitemap.xml\n", encoding="utf-8")
    (WURZEL / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    (WURZEL / "urls.txt").write_text("\n".join(urls) + "\n", encoding="utf-8")
    print("gebaut:", len(SEITEN), "Antwortseiten,", len(urls), "URLs")

if __name__ == "__main__":
    bauen()
