# Handleiding Solvigo CRM v8.1

## 1. Wat is het verschil tussen Partner, Klant en Project?

**Partner**
: Een installateur, O&M-bedrijf of andere partij die jou werk kan aanbrengen.

**Klant**
: Het bedrijf of de persoon waarvoor je effectief werkt of wil werken.

**Project**
: Een concrete opdracht, offerte, plaatsbezoek of reiniging bij een klant.

Voorbeeld:

```text
Partner: Kempen Solar
Klant: Janssens Agro
Project: Reiniging Janssens Agro 2026
```

Als Kempen Solar zegt: “Bel die klant eens”, maak je dus:

1. Kempen Solar als partner.
2. Janssens Agro als klant.
3. Reiniging Janssens Agro 2026 als project.
4. Automatische actie: eindklant contacteren.

## 2. Jaarlijkse klant

Een jaarlijkse klant blijft in **Klanten** staan.

Vul bijvoorbeeld in:

```text
Klant: Janssens Agro
Terugkerend: Ja
Frequentie: Jaarlijks
Status: Terugkerende klant
```

Elk jaar maak je een nieuw project:

```text
Reiniging Janssens Agro 2026
Reiniging Janssens Agro 2027
Reiniging Janssens Agro 2028
```

Wanneer je een project op **Uitgevoerd** zet, plant de app automatisch een jaarlijkse opvolging op klantniveau.

## 3. Projectstatussen en automatische acties

| Projectstatus | Automatische volgende actie |
|---|---|
| Nieuwe aanvraag | Eindklant contacteren |
| Te contacteren | Eindklant contacteren |
| Gecontacteerd | Info opvragen of plaatsbezoek voorstellen |
| Info gevraagd | Ontbrekende info opvragen |
| Plaatsbezoek plannen | Plaatsbezoek inplannen |
| Plaatsbezoek gepland | Plaatsbezoek uitvoeren |
| Plaatsbezoek uitgevoerd | Plaatsbezoekverslag maken |
| Verslag maken | Plaatsbezoekverslag maken |
| Verslag klaar | Offerte opmaken |
| Offerte maken | Offerte opmaken en versturen |
| Offerte verstuurd | Offerte opvolgen |
| Gewonnen | Uitvoering/reiniging inplannen |
| Uitvoering gepland | Uitvoering voorbereiden |
| Uitgevoerd | Jaarlijkse opvolging plannen |
| Verloren / No-go | Geen nieuwe actie |

## 4. Plaatsbezoek met foto's

Ga naar **Plaatsbezoek** en maak een verslag bij een project.

Foto's worden niet als bestand in Google Sheets opgeslagen. Upload ze naar Google Drive en plak de deel-links in het veld **Foto-links**.

Na opslaan kan de app de projectstatus automatisch op **Verslag klaar** zetten en een actie **Offerte opmaken** plannen.

## 5. Actieblad

Het actieblad is je dagelijkse werklijst. Daar zie je:

- te laat
- vandaag
- deze week
- later

Elke statuswijziging kan automatisch een actie aanmaken of bijwerken.

## 6. Oude data

Onder **Data & export** staan twee nuttige knoppen:

1. **Projectklanten aanmaken / koppelen**  
   Maakt klantfiches uit bestaande projecten zonder klant-ID.

2. **Oude Leads splitsen naar Partners + Klanten + Projecten**  
   Migreert oude leadtrackerdata naar de nieuwe CRM-structuur.

## v8.1 update

Het tabblad **Agenda** is teruggezet. Daar zie je acties op datum, kan je acties afronden, +3 dagen of +7 dagen uitstellen en opvolgreeksen/cadansen starten.

