# Handleiding — Solvigo Lead opvolging

Uitgebreide uitleg over wat de app doet, hoe je hem opzet, en hoe je hem gebruikt.

---

## 1. Wat de app doet

Een lichtgewicht CRM voor je cold outreach. De data staat in een Google Sheet,
de app is de bediening eromheen. Vijf tabbladen:

### 🔔 Opvolgen — je startscherm
Toont onmiddellijk:
- **⚠ Te laat** — leads waarvan de actiedatum voorbij is en die nog niet
  afgehandeld zijn. Dit is je prioriteitenlijst.
- **Deze week** — acties die binnen 7 dagen vallen.
- **Zonder datum** — leads die je nog geen volgende stap gaf (klapt open).

De logica: een lead met status *Gewonnen / Verloren / No-go* verdwijnt uit de
opvolging. Alle andere worden beoordeeld op hun *datum actie*.

### 📋 Alle leads — bewerkbare tabel
Spreadsheet-gevoel binnen de app: dropdowns voor type en status, datumvelden,
filters (status/type) en een zoekbalk. Bewerk rechtstreeks in de tabel, voeg
rijen toe onderaan, en klik op **Opslaan**. Nieuwe rijen krijgen automatisch een
ID. Er is ook een knop om alles naar Excel te exporteren.

### 👤 Lead — detailpagina
Werk aan één lead tegelijk:
- Alle velden bewerken in een net formulier (fijner op gsm dan de tabel).
- **Geschatte waarde** = aantal panelen × je richtprijs per paneel (zie zijbalk).
- **Offerte-brug** — een kopieerbaar blok met de leaddata, klaar om in je
  offerte-tool te plakken.
- **Contactmoment loggen** — noteer elke bel/mail/bezoek. Dit zet automatisch
  *laatste contact* op vandaag, en je kunt meteen de volgende actie + datum
  instellen. Een lead met status *Nieuw* springt automatisch op *Gecontacteerd*.
- **Historiek** — tijdlijn van alle contactmomenten.
- Lead (met logboek) verwijderen.

### ➕ Nieuwe lead — snel formulier
Eén lead in enkele tikken toevoegen. Ideaal onderweg.

### 📊 Dashboard
Totaal leads, actief in pijplijn, conversie (gewonnen ÷ gewonnen+verloren),
**pijplijnwaarde** (panelen × richtprijs), pipeline per status en panelen per
fase.

---

## 2. Eenmalige setup (± 15 minuten)

### Stap 1 — Google Sheet
Maak een lege Google Sheet aan. Kopieer het ID uit de URL:
`docs.google.com/spreadsheets/d/`**`DIT_STUK`**`/edit`
De app maakt zelf de tabbladen *Leads* en *Log* aan.

### Stap 2 — Service-account (hergebruik die van je offerte-app)
Je offerte-app gebruikt al een service-account. Gebruik exact hetzelfde:
- Open de JSON-sleutel en zoek het veld `client_email`.
- **Deel je nieuwe Sheet** met dat e-mailadres, rol **Bewerker**.

Geen service-account? Maak er een in Google Cloud → *IAM & Admin* →
*Service Accounts* → sleutel (JSON) downloaden. Zet in je project de
**Google Sheets API** én **Google Drive API** aan.

### Stap 3 — Repo
```bash
git init
git add .
git commit -m "Solvigo lead tracker"
gh repo create solvigo-leadtracker --private --source=. --push
```

### Stap 4 — Deploy
Ga naar share.streamlit.io → *New app* → kies je repo, branch `main`,
bestand `app.py`.

### Stap 5 — Secrets
Bij *Advanced settings → Secrets* (of later via *Settings → Secrets*) plak je de
inhoud van `.streamlit/secrets.toml.example`, met je eigen waarden. Het
`[gcp_service_account]`-blok is identiek aan dat van je offerte-app — kopieer
het gewoon over. Alleen `[sheet].id` verschilt.

---

## 3. Dagelijks gebruik

1. Open de app → tab **🔔 Opvolgen**. Werk je *Te laat*-lijst af.
2. Na elk belletje/mailtje: ga naar **👤 Lead**, log het contactmoment en zet
   meteen de volgende actie + datum. Zo blijft je opvolging vanzelf lopen.
3. Nieuwe prospect onderweg? Tab **➕ Nieuwe lead**.
4. Wekelijks even **📊 Dashboard** checken voor je pijplijnwaarde.

Omdat er geen automatische herinneringen zijn, is de gewoonte belangrijk: zet
één vast moment per week (bv. maandagochtend) om de app te openen.

---

## 4. Goed om te weten

- **Opslaan overschrijft het hele tabblad** (last-write-wins). Voor solo-gebruik
  prima. Heb je de Sheet ergens anders tegelijk open en bewerkt, dan wint wie
  het laatst opslaat.
- **Data cachet 30 seconden** om Google's API-limiet te sparen. Zie je een
  wijziging niet meteen? Klik **🔄 Data vernieuwen** in de zijbalk.
- **Datums** worden opgeslagen als `JJJJ-MM-DD`. Hernoem de kolomkoppen in de
  Sheet niet — de app verwacht exact deze namen.
- **Richtprijs per paneel** (zijbalk) is enkel voor de waardeschatting; hij
  wordt niet opgeslagen en verandert niks aan je echte offertes.

---

## 5. Kolommen

**Leads:** `id, bedrijf, type, contactpersoon, functie, email, telefoon, regio,
aantal_panelen, bron, status, eerste_contact, laatste_contact, volgende_actie,
datum_actie, notities`

**Log:** `id, lead_id, datum, soort, notitie`

---

## 6. Mogelijke uitbreidingen

- Automatische ochtendmail met je *Te laat*-lijst (via een aparte cron/Actions).
- Echte offerte-PDF genereren vanuit de detailpagina (koppelen aan je bestaande
  offerte-tool i.p.v. de kopieer-brug).
- Kaartweergave van leads op basis van regio.
