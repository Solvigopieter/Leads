"""Constanten, kolomdefinities en labels voor de lead-tracker."""

WS_LEADS = "Leads"
WS_LOG = "Log"

TYPES = ["Installateur", "O&M", "Eindklant industrieel", "Eindklant landbouw", "Andere"]

STATUSES = ["Nieuw", "Gecontacteerd", "Opvolgen", "Interesse / gesprek",
            "Offerte verstuurd", "Gewonnen", "Verloren", "No-go"]
AFGEHANDELD = {"Gewonnen", "Verloren", "No-go"}
ACTIEF = [s for s in STATUSES if s not in AFGEHANDELD]

SOORTEN = ["Telefoon", "E-mail", "Bezoek", "Notitie", "Offerte"]

LEAD_HEADERS = ["id", "bedrijf", "type", "contactpersoon", "functie", "email",
                "telefoon", "regio", "aantal_panelen", "bron", "status",
                "eerste_contact", "laatste_contact", "volgende_actie",
                "datum_actie", "notities"]
LOG_HEADERS = ["id", "lead_id", "datum", "soort", "notitie"]

DATE_COLS = ["eerste_contact", "laatste_contact", "datum_actie"]

LABELS = {
    "id": "ID", "bedrijf": "Bedrijf", "type": "Type", "contactpersoon": "Contact",
    "functie": "Functie", "email": "E-mail", "telefoon": "Telefoon",
    "regio": "Regio", "aantal_panelen": "# Panelen", "bron": "Bron",
    "status": "Status", "eerste_contact": "1e contact",
    "laatste_contact": "Laatste contact", "volgende_actie": "Volgende actie",
    "datum_actie": "Datum actie", "notities": "Notities",
    "lead_id": "Lead", "datum": "Datum", "soort": "Soort", "notitie": "Notitie",
}

STATUS_KLEUR = {
    "Nieuw": "#E5E7EB", "Gecontacteerd": "#DBEAFE", "Opvolgen": "#FEF3C7",
    "Interesse / gesprek": "#D1FAE5", "Offerte verstuurd": "#C7D2FE",
    "Gewonnen": "#BBF7D0", "Verloren": "#FEE2E2", "No-go": "#E5E7EB",
}
