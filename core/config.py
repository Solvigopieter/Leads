"""Constanten, kolommen en workflowregels voor de Solvigo CRM-app."""

# Google Sheet tabbladen
WS_PARTNERS = "Partners"
WS_CUSTOMERS = "Klanten"
WS_PROJECTS = "Projecten"
WS_ACTIONS = "Acties"
WS_VISITS = "Plaatsbezoeken"
WS_LOG = "Log"
WS_LEGACY_LEADS = "Leads"

# ----------------------------- partners / bronnen
PARTNER_TYPES = ["Installateur", "O&M", "EPC / advies", "Vastgoedbeheer", "Andere partner"]
PARTNER_STATUSES = [
    "Nieuw",
    "Te contacteren",
    "Gecontacteerd",
    "Interesse samenwerking",
    "Actieve partner",
    "Slapend",
    "Niet interessant",
]
PARTNER_AFGEHANDELD = {"Niet interessant"}
PARTNER_HEADERS = [
    "id", "bedrijf", "type", "contactpersoon", "functie", "email", "telefoon", "regio", "website",
    "status", "bron", "eerste_contact", "laatste_contact", "volgende_actie", "datum_actie", "notities",
]

# ----------------------------- klanten
CUSTOMER_TYPES = ["Bedrijf", "Landbouw", "Particulier", "Vastgoedbeheer", "Openbaar bestuur", "Andere"]
CUSTOMER_STATUSES = [
    "Prospect",
    "Te contacteren",
    "Actieve klant",
    "Terugkerende klant",
    "Slapend",
    "Niet interessant",
]
CUSTOMER_AFGEHANDELD = {"Niet interessant"}
CUSTOMER_HEADERS = [
    "id", "klant_bedrijf", "type", "contactpersoon", "email", "telefoon", "adres", "regio",
    "status", "bron_type", "partner_id", "partner_bedrijf", "terugkerend", "frequentie",
    "laatste_reiniging", "volgende_contact", "laatste_contact", "volgende_actie", "datum_actie", "notities",
]

# ----------------------------- projecten / deals
# Dit is bewust dichter bij professionele CRM's: een project gaat van nieuwe aanvraag naar uitvoering.
PROJECT_STATUSES = [
    "Nieuwe aanvraag",
    "Te contacteren",
    "Gecontacteerd",
    "Info gevraagd",
    "Plaatsbezoek plannen",
    "Plaatsbezoek gepland",
    "Plaatsbezoek uitgevoerd",
    "Verslag maken",
    "Verslag klaar",
    "Offerte maken",
    "Offerte verstuurd",
    "Gewonnen",
    "Uitvoering gepland",
    "Uitgevoerd",
    "Jaarlijkse opvolging",
    "Verloren",
    "No-go",
]
PROJECT_AFGEHANDELD = {"Uitgevoerd", "Verloren", "No-go"}

# Winstkans per fase -> gewogen pijplijnwaarde
STAGE_PROBABILITY = {
    "Nieuwe aanvraag": 0.10,
    "Te contacteren": 0.10,
    "Gecontacteerd": 0.15,
    "Info gevraagd": 0.20,
    "Plaatsbezoek plannen": 0.25,
    "Plaatsbezoek gepland": 0.35,
    "Plaatsbezoek uitgevoerd": 0.45,
    "Verslag maken": 0.50,
    "Verslag klaar": 0.55,
    "Offerte maken": 0.60,
    "Offerte verstuurd": 0.65,
    "Gewonnen": 0.90,
    "Uitvoering gepland": 0.95,
    "Uitgevoerd": 1.0,
    "Jaarlijkse opvolging": 0.25,
    "Verloren": 0.0,
    "No-go": 0.0,
}

# Deal rotting: aantal dagen zonder contact voor een project 'verschraalt'
ROTTING_DAYS = {
    "Nieuwe aanvraag": 3,
    "Te contacteren": 4,
    "Gecontacteerd": 7,
    "Info gevraagd": 7,
    "Plaatsbezoek plannen": 7,
    "Plaatsbezoek gepland": 10,
    "Plaatsbezoek uitgevoerd": 3,
    "Verslag maken": 3,
    "Verslag klaar": 3,
    "Offerte maken": 3,
    "Offerte verstuurd": 7,
    "Gewonnen": 7,
    "Uitvoering gepland": 14,
    "Jaarlijkse opvolging": 60,
}
ROTTING_DEFAULT = 14

KANBAN_STAGES = [
    "Nieuwe aanvraag", "Gecontacteerd", "Plaatsbezoek gepland", "Verslag klaar",
    "Offerte maken", "Offerte verstuurd", "Gewonnen", "Uitvoering gepland", "Uitgevoerd",
]

# Nieuwe kolommen staan bewust achteraan, zodat bestaande Projecten-data niet verschuift.
PROJECT_HEADERS = [
    "id", "projectnaam", "klant_bedrijf", "contactpersoon", "email", "telefoon", "adres", "regio",
    "aantal_panelen", "partner_id", "partner_bedrijf", "bron_type", "status", "eerste_contact",
    "laatste_contact", "volgende_actie", "datum_actie", "verwachte_waarde", "notities",
    "klant_id", "terugkerend", "frequentie", "hercontactdatum",
]

BRON_TYPES = [
    "Los project",
    "Doorverwijzing installateur",
    "Doorverwijzing O&M",
    "Doorverwijzing klant",
    "Bestaande klant",
    "Google Maps",
    "LinkedIn",
    "Website",
    "Andere",
]

# ----------------------------- automatische workflow
PROJECT_STATUS_NEXT_ACTION = {
    "Nieuwe aanvraag": {"actie": "Eindklant contacteren", "dagen": 1, "kanaal": "Telefoon", "prioriteit": "Hoog"},
    "Te contacteren": {"actie": "Eindklant contacteren", "dagen": 1, "kanaal": "Telefoon", "prioriteit": "Hoog"},
    "Gecontacteerd": {"actie": "Info opvragen of plaatsbezoek voorstellen", "dagen": 2, "kanaal": "Telefoon", "prioriteit": "Normaal"},
    "Info gevraagd": {"actie": "Ontbrekende info opvragen", "dagen": 3, "kanaal": "E-mail", "prioriteit": "Normaal"},
    "Plaatsbezoek plannen": {"actie": "Plaatsbezoek inplannen", "dagen": 2, "kanaal": "Telefoon", "prioriteit": "Hoog"},
    "Plaatsbezoek gepland": {"actie": "Plaatsbezoek uitvoeren", "dagen": 0, "kanaal": "Plaatsbezoek", "prioriteit": "Hoog"},
    "Plaatsbezoek uitgevoerd": {"actie": "Plaatsbezoekverslag maken", "dagen": 1, "kanaal": "Administratie", "prioriteit": "Hoog"},
    "Verslag maken": {"actie": "Plaatsbezoekverslag maken", "dagen": 1, "kanaal": "Administratie", "prioriteit": "Hoog"},
    "Verslag klaar": {"actie": "Offerte opmaken", "dagen": 1, "kanaal": "Offerte", "prioriteit": "Hoog"},
    "Offerte maken": {"actie": "Offerte opmaken en versturen", "dagen": 1, "kanaal": "Offerte", "prioriteit": "Hoog"},
    "Offerte verstuurd": {"actie": "Offerte opvolgen", "dagen": 7, "kanaal": "Telefoon", "prioriteit": "Normaal"},
    "Gewonnen": {"actie": "Uitvoering/reiniging inplannen", "dagen": 2, "kanaal": "Telefoon", "prioriteit": "Hoog"},
    "Uitvoering gepland": {"actie": "Uitvoering voorbereiden", "dagen": 2, "kanaal": "Administratie", "prioriteit": "Normaal"},
    "Uitgevoerd": {"actie": "Jaarlijkse opvolging plannen", "dagen": 330, "kanaal": "E-mail", "prioriteit": "Normaal"},
    "Jaarlijkse opvolging": {"actie": "Klant opnieuw contacteren voor reiniging", "dagen": 0, "kanaal": "Telefoon", "prioriteit": "Normaal"},
    "Verloren": {"actie": "", "dagen": 0, "kanaal": "Andere", "prioriteit": "Laag"},
    "No-go": {"actie": "", "dagen": 0, "kanaal": "Andere", "prioriteit": "Laag"},
}

PARTNER_STATUS_NEXT_ACTION = {
    "Nieuw": {"actie": "Partner contacteren", "dagen": 2, "kanaal": "Telefoon", "prioriteit": "Normaal"},
    "Te contacteren": {"actie": "Samenwerking voorstellen", "dagen": 3, "kanaal": "Telefoon", "prioriteit": "Normaal"},
    "Gecontacteerd": {"actie": "Samenwerking opvolgen", "dagen": 7, "kanaal": "Telefoon", "prioriteit": "Normaal"},
    "Interesse samenwerking": {"actie": "Afspraak of proefproject voorstellen", "dagen": 3, "kanaal": "E-mail", "prioriteit": "Hoog"},
    "Actieve partner": {"actie": "Partner check-in / nieuwe projecten vragen", "dagen": 30, "kanaal": "Telefoon", "prioriteit": "Normaal"},
    "Slapend": {"actie": "Partner heractiveren", "dagen": 30, "kanaal": "E-mail", "prioriteit": "Laag"},
    "Niet interessant": {"actie": "", "dagen": 0, "kanaal": "Andere", "prioriteit": "Laag"},
}

CUSTOMER_STATUS_NEXT_ACTION = {
    "Prospect": {"actie": "Klant contacteren", "dagen": 1, "kanaal": "Telefoon", "prioriteit": "Hoog"},
    "Te contacteren": {"actie": "Klant contacteren", "dagen": 1, "kanaal": "Telefoon", "prioriteit": "Hoog"},
    "Actieve klant": {"actie": "Nazorg / tevredenheid checken", "dagen": 30, "kanaal": "E-mail", "prioriteit": "Normaal"},
    "Terugkerende klant": {"actie": "Opnieuw contacteren voor jaarlijkse reiniging", "dagen": 330, "kanaal": "Telefoon", "prioriteit": "Normaal"},
    "Slapend": {"actie": "Klant heractiveren", "dagen": 30, "kanaal": "Telefoon", "prioriteit": "Laag"},
    "Niet interessant": {"actie": "", "dagen": 0, "kanaal": "Andere", "prioriteit": "Laag"},
}

# ----------------------------- actieblad
ACTION_STATUSES = ["Open", "Gedaan", "Uitgesteld", "Geannuleerd"]
ACTION_PRIORITIES = ["Hoog", "Normaal", "Laag"]
ACTION_CHANNELS = ["Telefoon", "E-mail", "WhatsApp", "Plaatsbezoek", "Offerte", "Administratie", "Andere"]
ACTION_HEADERS = [
    "id", "relatie_type", "relatie_id", "relatie_naam", "actie", "datum_actie", "prioriteit", "status",
    "kanaal", "notities", "aangemaakt_op", "afgerond_op", "cadans", "cadans_stap",
]

# ----------------------------- cadans
CADANS = {
    "Standaard outreach": [
        {"label": "1e mail sturen", "kanaal": "E-mail", "wacht": 0},
        {"label": "Opvolgmail sturen", "kanaal": "E-mail", "wacht": 4},
        {"label": "Bellen voor reactie", "kanaal": "Telefoon", "wacht": 4},
        {"label": "Plaatsbezoek inplannen", "kanaal": "Plaatsbezoek", "wacht": 7},
        {"label": "Offerte opmaken en versturen", "kanaal": "Offerte", "wacht": 5},
        {"label": "Offerte opvolgen", "kanaal": "Telefoon", "wacht": 7},
        {"label": "Laatste follow-up", "kanaal": "E-mail", "wacht": 10},
    ],
    "Bestaande klant heractiveren": [
        {"label": "Heractivatie-mail sturen", "kanaal": "E-mail", "wacht": 0},
        {"label": "Bellen", "kanaal": "Telefoon", "wacht": 5},
        {"label": "Nieuwe offerte voorstellen", "kanaal": "Offerte", "wacht": 5},
        {"label": "Offerte opvolgen", "kanaal": "Telefoon", "wacht": 7},
    ],
    "Snel (warme lead)": [
        {"label": "Bellen voor afspraak", "kanaal": "Telefoon", "wacht": 0},
        {"label": "Plaatsbezoek", "kanaal": "Plaatsbezoek", "wacht": 5},
        {"label": "Offerte versturen", "kanaal": "Offerte", "wacht": 3},
        {"label": "Offerte opvolgen", "kanaal": "Telefoon", "wacht": 5},
    ],
}

# ----------------------------- plaatsbezoeken
VISIT_HEADERS = [
    "id", "project_id", "projectnaam", "datum", "contact_ter_plaatse", "adres",
    "aantal_panelen_gezien", "dak_type", "helling", "vervuiling", "toegang", "waterpunt",
    "veiligheid", "verslag", "foto_links", "volgende_actie", "datum_actie", "aangemaakt_op",
]
VISIT_DAK_TYPES = ["Plat dak", "Hellend dak", "Grondopstelling", "Carport", "Gemengd", "Onbekend"]
VISIT_VERVUILING = ["Licht", "Normaal", "Sterk", "Korstmos / algen", "Onbekend"]
VISIT_TOEGANG = ["Goed", "Ladder nodig", "Hoogtewerker nodig", "Daktoegang aanwezig", "Nog te controleren"]

# ----------------------------- logboek
LOG_SOORTEN = ["Telefoon", "E-mail", "WhatsApp", "Bezoek", "Notitie", "Offerte", "Doorverwijzing"]
LOG_HEADERS = ["id", "relatie_type", "relatie_id", "relatie_naam", "datum", "soort", "notitie"]

# ----------------------------- datatypes
DATE_COLS = {
    WS_PARTNERS: ["eerste_contact", "laatste_contact", "datum_actie"],
    WS_CUSTOMERS: ["laatste_reiniging", "volgende_contact", "laatste_contact", "datum_actie"],
    WS_PROJECTS: ["eerste_contact", "laatste_contact", "datum_actie", "hercontactdatum"],
    WS_ACTIONS: ["datum_actie", "aangemaakt_op", "afgerond_op"],
    WS_VISITS: ["datum", "datum_actie", "aangemaakt_op"],
    WS_LOG: ["datum"],
    WS_LEGACY_LEADS: ["eerste_contact", "laatste_contact", "datum_actie"],
}
INT_COLS = {
    WS_PARTNERS: [],
    WS_CUSTOMERS: [],
    WS_PROJECTS: ["aantal_panelen"],
    WS_ACTIONS: [],
    WS_VISITS: ["aantal_panelen_gezien"],
    WS_LOG: [],
    WS_LEGACY_LEADS: ["aantal_panelen"],
}
FLOAT_COLS = {WS_PROJECTS: ["verwachte_waarde"]}

# ----------------------------- oude leadtracker-migratie
LEGACY_LEAD_HEADERS = [
    "id", "bedrijf", "type", "contactpersoon", "functie", "email", "telefoon", "regio",
    "aantal_panelen", "bron", "status", "eerste_contact", "laatste_contact",
    "volgende_actie", "datum_actie", "notities",
]
LEGACY_PARTNER_TYPES = {"Installateur", "O&M"}

# ----------------------------- labels
LABELS = {
    "id": "ID",
    "bedrijf": "Bedrijf",
    "klant_bedrijf": "Klant",
    "type": "Type",
    "contactpersoon": "Contactpersoon",
    "functie": "Functie",
    "email": "E-mail",
    "telefoon": "Telefoon",
    "regio": "Regio",
    "website": "Website",
    "status": "Status",
    "bron": "Bron",
    "bron_type": "Bron type",
    "eerste_contact": "Eerste contact",
    "laatste_contact": "Laatste contact",
    "volgende_actie": "Volgende actie",
    "datum_actie": "Datum actie",
    "notities": "Notities",
    "projectnaam": "Project",
    "adres": "Adres",
    "aantal_panelen": "# panelen",
    "partner_id": "Partner-ID",
    "partner_bedrijf": "Partner",
    "klant_id": "Klant-ID",
    "terugkerend": "Terugkerend",
    "frequentie": "Frequentie",
    "laatste_reiniging": "Laatste reiniging",
    "volgende_contact": "Volgende contact",
    "hercontactdatum": "Hercontactdatum",
    "verwachte_waarde": "Verwachte waarde",
    "relatie_type": "Relatie type",
    "relatie_id": "Relatie-ID",
    "relatie_naam": "Relatie",
    "actie": "Actie",
    "prioriteit": "Prioriteit",
    "kanaal": "Kanaal",
    "aangemaakt_op": "Aangemaakt op",
    "afgerond_op": "Afgerond op",
    "cadans": "Cadans",
    "cadans_stap": "Stap",
    "project_id": "Project-ID",
    "datum": "Datum",
    "contact_ter_plaatse": "Contact ter plaatse",
    "aantal_panelen_gezien": "Panelen gezien",
    "dak_type": "Daktype",
    "helling": "Helling",
    "vervuiling": "Vervuiling",
    "toegang": "Toegang",
    "waterpunt": "Waterpunt",
    "veiligheid": "Veiligheid",
    "verslag": "Verslag",
    "foto_links": "Foto-links",
    "soort": "Soort",
    "notitie": "Notitie",
}

STATUS_KLEUR = {
    "Nieuw": "#E5E7EB",
    "Prospect": "#E5E7EB",
    "Te contacteren": "#FEF3C7",
    "Gecontacteerd": "#DBEAFE",
    "Interesse samenwerking": "#D1FAE5",
    "Actieve partner": "#BBF7D0",
    "Actieve klant": "#BBF7D0",
    "Terugkerende klant": "#DCFCE7",
    "Slapend": "#EDE9FE",
    "Niet interessant": "#FEE2E2",
    "Nieuwe aanvraag": "#E5E7EB",
    "Info gevraagd": "#DBEAFE",
    "Plaatsbezoek plannen": "#E0F2FE",
    "Plaatsbezoek gepland": "#C7D2FE",
    "Plaatsbezoek uitgevoerd": "#D1FAE5",
    "Verslag maken": "#FEF3C7",
    "Verslag klaar": "#FDE68A",
    "Offerte maken": "#FDE68A",
    "Offerte verstuurd": "#DDD6FE",
    "Gewonnen": "#BBF7D0",
    "Uitvoering gepland": "#A7F3D0",
    "Uitgevoerd": "#86EFAC",
    "Jaarlijkse opvolging": "#CCFBF1",
    "Verloren": "#FEE2E2",
    "No-go": "#E5E7EB",
    "Open": "#FEF3C7",
    "Gedaan": "#BBF7D0",
    "Uitgesteld": "#DBEAFE",
    "Geannuleerd": "#FEE2E2",
}
