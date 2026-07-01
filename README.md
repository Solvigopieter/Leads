# Solvigo CRM v8.1

Professionele Streamlit CRM voor Solvigo met aparte tabbladen voor:

- Partners / installateurs
- Klanten
- Projecten / opdrachten
- Acties
- Plaatsbezoeken
- Logboek

## v8.1 update

Het tabblad **Agenda** is teruggezet. Daar zie je acties op datum, kan je acties afronden, +3 dagen of +7 dagen uitstellen en opvolgreeksen/cadansen starten.

## Belangrijkste wijziging in v8

De CRM-structuur volgt nu beter de manier waarop bekende CRM's werken:

```text
Partner / installateur -> brengt werk aan
Klant -> bedrijf of persoon waarvoor je werkt
Project -> concrete offerte, reiniging of plaatsbezoek
Actie -> volgende stap met datum
Plaatsbezoek -> verslag + foto-links
```

Een jaarlijkse klant wordt dus geen partner. Die klant blijft in **Klanten** staan. Elk jaar maak je een nieuw **Project** voor die klant.

## Professionele projectflow

```text
Nieuwe aanvraag
-> Eindklant contacteren

Gecontacteerd
-> Info opvragen of plaatsbezoek voorstellen

Info gevraagd
-> Ontbrekende info opvragen

Plaatsbezoek plannen
-> Plaatsbezoek inplannen

Plaatsbezoek gepland
-> Plaatsbezoek uitvoeren

Plaatsbezoek uitgevoerd
-> Plaatsbezoekverslag maken

Verslag klaar
-> Offerte opmaken

Offerte maken
-> Offerte opmaken en versturen

Offerte verstuurd
-> Offerte opvolgen na 7 dagen

Gewonnen
-> Uitvoering/reiniging inplannen

Uitvoering gepland
-> Uitvoering voorbereiden

Uitgevoerd
-> Jaarlijkse opvolging plannen

Verloren / No-go
-> Geen nieuwe open actie
```

Als je een status wijzigt en opslaat, past de app automatisch aan:

- volgende actie
- datum actie
- actieblad
- logboek

Bij status **Uitgevoerd** wordt de gekoppelde klant automatisch bijgewerkt. Is het een terugkerende klant, dan plant de app een jaarlijkse opvolging.

## Streamlit Secrets

Gebruik dezelfde secrets als je offerte-app, plus je Sheet-ID:

```toml
[sheet]
id = "JE_GOOGLE_SHEET_ID"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

## Bestanden deployen

Vervang in GitHub minstens:

```text
app.py
core/config.py
core/logic.py
core/sheets.py
README.md
HANDLEIDING.md
```

Daarna committen en de Streamlit-app rebooten.


## v8.3 fix

Agenda-fout opgelost: `cadans_stappen` wordt nu correct geïmporteerd, waardoor het tabblad Agenda opnieuw opent.


## v8.3 fix
- Acties afronden en uitstellen bewaart datums nu als ISO-tekst, zodat pandas/Streamlit niet crasht op datumkolommen.
