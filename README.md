# Solvigo CRM — partners, projecten, actieblad en plaatsbezoeken

Streamlit-app voor Solvigo leadopvolging met Google Sheets als backend.

## Nieuwe structuur

De app maakt bewust een onderscheid tussen:

- **Partners**: installateurs, O&M-partijen en andere bedrijven die werk kunnen aanbrengen.
- **Projecten**: concrete reinigingsopdrachten/eindklanten.
- **Acties**: dagelijkse opvolglijst: wie moet opnieuw gecontacteerd worden en wanneer.
- **Plaatsbezoeken**: verslag per project, inclusief technische observaties en foto-links.
- **Log**: historiek van contactmomenten.

Voorbeeld: een installateur zegt “neem contact op met die klant”.
Dan blijft de installateur in **Partners**, en maak je vanuit de partnerfiche een apart **Project** aan. De app maakt meteen een actie aan om de eindklant te contacteren.

## Setup

1. Maak of gebruik een Google Sheet.
2. Deel de Sheet met het service-account als **Bewerker**.
3. Deploy op Streamlit Community Cloud met `app.py` als main file.
4. Zet bij Streamlit Secrets:

```toml
[sheet]
id = "JOUW_GOOGLE_SHEET_ID"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "...@...iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

De app maakt automatisch deze tabbladen aan in Google Sheets:

```text
Partners
Projecten
Acties
Plaatsbezoeken
Log
```

## Foto's bij plaatsbezoek

Google Sheets is niet geschikt als fotomap. De app bewaart daarom foto-links:

1. Upload foto’s naar Google Drive.
2. Zet delen aan voor wie ze moet bekijken.
3. Plak de links in het veld **Foto-links** bij het plaatsbezoek.

## Oude leadtracker-data

Had je al een oud tabblad `Leads`? Ga naar **Data & export** en klik op **Oude Leads splitsen naar Partners + Projecten**. Het oude tabblad blijft bestaan als backup.
