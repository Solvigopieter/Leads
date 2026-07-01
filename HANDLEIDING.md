# Handleiding — Solvigo CRM

## Dagelijks gebruik

Start elke werkdag in **Actieblad**.

De belangrijkste blokken zijn:

1. **Te laat**: eerst oplossen.
2. **Vandaag**: daarna afwerken.
3. **Deze week**: voorbereiden en opvolgen.

Na elk telefoontje of mailtje log je een contactmoment en zet je meteen een volgende actie met datum. Zo blijft je opvolging automatisch georganiseerd.

## Partners versus projecten

### Partners

Partners zijn installateurs, O&M-partijen of andere bedrijven die jou projecten kunnen aanbrengen.

Gebruik Partners voor:

- installateurs die je wil benaderen;
- bedrijven die regelmatig klanten kunnen doorverwijzen;
- O&M-partijen met grote portefeuilles;
- samenwerkingsgesprekken.

### Projecten

Projecten zijn concrete opdrachten of eindklanten.

Gebruik Projecten voor:

- één bedrijf met zonnepanelen die gereinigd moeten worden;
- een klant die door een installateur werd doorgestuurd;
- een plaatsbezoek;
- een offerte en opvolging.

## Doorverwijzing door installateur

Als een installateur zegt “neem contact op met die persoon”:

1. Ga naar **Partners**.
2. Kies de installateur.
3. Open **Project aanmaken uit doorverwijzing**.
4. Vul de klantgegevens in.
5. Klik op **Doorverwezen project toevoegen**.

De app maakt dan automatisch:

- een project voor de klant;
- een actie om de klant te contacteren;
- een logitem bij de partner.

## Plaatsbezoekverslag

Ga naar **Plaatsbezoek** en maak een verslag bij een project.

Vul onder andere in:

- datum;
- contact ter plaatse;
- adres;
- aantal panelen;
- daktype;
- vervuiling;
- toegang;
- waterpunt;
- veiligheid;
- verslagtekst;
- foto-links;
- volgende actie.

Na opslaan maakt de app automatisch een vervolgactie, bijvoorbeeld **Offerte maken**.

## Foto's

De app bewaart foto’s als links. Upload foto’s naar Google Drive en plak de links bij **Foto-links**. Dat is betrouwbaarder dan foto’s in Google Sheets proberen te bewaren.

## Excel-export

Ga naar **Data & export** en klik op **Exporteer volledige CRM naar Excel**. De export bevat aparte werkbladen voor Partners, Projecten, Acties, Plaatsbezoeken en Log.

---

## Nieuw: Agenda + automatische opvolgreeksen (cadans)

### Cadans — je opvolging plant zichzelf in
Een *cadans* is een vaste opvolgvolgorde. Je start ze één keer; daarna verschijnt
telkens de volgende stap automatisch zodra je de vorige afvinkt.

Ingebouwde reeksen (aan te passen in `core/config.py` onder `CADANS`):
- **Standaard outreach:** 1e mail → opvolgmail (+4d) → bellen (+4d) →
  plaatsbezoek (+7d) → offerte (+5d) → offerte opvolgen (+7d) → laatste follow-up (+10d)
- **Bestaande klant heractiveren**
- **Snel (warme lead)**

De `+Xd` is het aantal dagen ná het afvinken van de vorige stap.

### Zo gebruik je het
1. Tab **🗓 Agenda** → **🔁 Opvolgreeks starten** → kies partner/project + reeks +
   startdatum → *Reeks starten*. Stap 1 staat nu in je agenda.
2. Werk je acties af met de **✓ Afronden**-knop. Dan gebeurt automatisch:
   - de actie gaat op *Gedaan* en komt in het Log;
   - de **volgende stap** wordt ingepland op de juiste datum.
3. Nog niet toe aan een actie? Gebruik **+3d** of **+7d** om ze uit te stellen.

### Agenda-tab
- **Komende 14 dagen:** strip met per dag het aantal geplande acties; dag 0 toont
  ook hoeveel er te laat zijn.
- **Te laat / Vandaag / Deze week:** je werklijst met afrond- en uitstelknoppen.
- **Later gepland:** klapt open voor alles verderop.

### Belangrijk
- De cadans loopt automatisch door zolang je afvinkt via **✓ Afronden**. Zet je een
  actie handmatig op *Gedaan* in het Actieblad-tabblad, dan wordt de volgende stap
  **niet** aangemaakt (bewust, om dubbels te vermijden). Gebruik dus de Afronden-knop.
- Cadans-info staat in twee nieuwe kolommen op het Acties-blad: `cadans` en
  `cadans_stap`. Niet handmatig aanpassen.
