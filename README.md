# Solvigo — Lead opvolging

Standalone Streamlit-app om leads op te volgen, met Google Sheets als backend
(zelfde gspread/google-auth-stack als je offerte-app).

## Snelstart
1. Maak een lege Google Sheet → kopieer het **Sheet-ID** uit de URL.
2. Deel die Sheet met het `client_email` van je service-account (rol: **Bewerker**).
3. Push deze map naar een nieuwe GitHub-repo.
4. Deploy op [share.streamlit.io](https://share.streamlit.io) → app-bestand `app.py`.
5. Bij **Settings → Secrets** plak je de inhoud van `.streamlit/secrets.toml.example`
   (met je eigen waarden). Klaar.

De app maakt zelf de tabbladen "Leads" en "Log" met de juiste kolommen aan.

## Lokaal draaien
```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # en invullen
streamlit run app.py
```

Uitgebreide uitleg: zie **HANDLEIDING.md**.

## Structuur
```
app.py                 hoofdapp met alle tabbladen
core/config.py         kolommen, statussen, labels
core/logic.py          opvolg-logica, waardeberekening, offerte-tekst
core/sheets.py         Google Sheets lezen/schrijven
requirements.txt
.streamlit/            thema + secrets-voorbeeld
```
