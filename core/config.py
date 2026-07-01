"""Constanten, kolommen en labels voor de Solvigo CRM-app."""

# Google Sheet tabbladen
WS_PARTNERS = "Partners"
WS_PROJECTS = "Projecten"
WS_ACTIONS = "Acties"
WS_VISITS = "Plaatsbezoeken"
WS_LOG = "Log"
WS_LEGACY_LEADS = "Leads"

# ----------------------------- partners
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

# ----------------------------- projecten
PROJECT_STATUSES = [
    "Nieuwe aanvraag",
    "Te contacteren",
    "Info gevraagd",
    "Plaatsbezoek gepland",
    "Verslag maken",
    "Offerte maken",
    "Offerte verstuurd",
    "Gewonnen",
    "Verloren",
    "No-go",
]
PROJECT_AFGEHANDELD = {"Gewonnen", "Verloren", "No-go"}
PROJECT_HEADERS = [
    "id", "projectnaam", "klant_bedrijf", "contactpersoon", "email", "telefoon", "adres", "regio",
    "aantal_panelen", "partner_id", "partner_bedrijf", "bron_type", "status", "eerste_contact",
    "laatste_contact", "volgende_actie", "datum_actie", "verwachte_waarde", "notities",
]
BRON_TYPES = [
    "Los project",
    "Doorverwijzing installateur",
    "Doorverwijzing O&M",
    "Bestaande klant",
    "Google Maps",
    "LinkedIn",
    "Website",
    "Andere",
]

# ----------------------------- actieblad
ACTION_STATUSES = ["Open", "Gedaan", "Uitgesteld", "Geannuleerd"]
ACTION_PRIORITIES = ["Hoog", "Normaal", "Laag"]
ACTION_CHANNELS = ["Telefoon", "E-mail", "WhatsApp", "Plaatsbezoek", "Offerte", "Administratie", "Andere"]
ACTION_HEADERS = [
    "id", "relatie_type", "relatie_id", "relatie_naam", "actie", "datum_actie", "prioriteit", "status",
    "kanaal", "notities", "aangemaakt_op", "afgerond_op",
]

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

# ----------------------------- datum/numeriek
DATE_COLS = {
    WS_PARTNERS: ["eerste_contact", "laatste_contact", "datum_actie"],
    WS_PROJECTS: ["eerste_contact", "laatste_contact", "datum_actie"],
    WS_ACTIONS: ["datum_actie", "aangemaakt_op", "afgerond_op"],
    WS_VISITS: ["datum", "datum_actie", "aangemaakt_op"],
    WS_LOG: ["datum"],
    WS_LEGACY_LEADS: ["eerste_contact", "laatste_contact", "datum_actie"],
}
INT_COLS = {
    WS_PARTNERS: [],
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
    "type": "Type",
    "contactpersoon": "Contactpersoon",
    "functie": "Functie",
    "email": "E-mail",
    "telefoon": "Telefoon",
    "regio": "Regio",
    "website": "Website",
    "status": "Status",
    "bron": "Bron",
    "eerste_contact": "Eerste contact",
    "laatste_contact": "Laatste contact",
    "volgende_actie": "Volgende actie",
    "datum_actie": "Datum actie",
    "notities": "Notities",
    "projectnaam": "Project",
    "klant_bedrijf": "Klantbedrijf",
    "adres": "Adres",
    "aantal_panelen": "# panelen",
    "partner_id": "Partner-ID",
    "partner_bedrijf": "Partner",
    "bron_type": "Bron type",
    "verwachte_waarde": "Verwachte waarde",
    "relatie_type": "Relatie type",
    "relatie_id": "Relatie-ID",
    "relatie_naam": "Relatie",
    "actie": "Actie",
    "prioriteit": "Prioriteit",
    "kanaal": "Kanaal",
    "aangemaakt_op": "Aangemaakt op",
    "afgerond_op": "Afgerond op",
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
    "Te contacteren": "#FEF3C7",
    "Gecontacteerd": "#DBEAFE",
    "Interesse samenwerking": "#D1FAE5",
    "Actieve partner": "#BBF7D0",
    "Slapend": "#EDE9FE",
    "Niet interessant": "#FEE2E2",
    "Nieuwe aanvraag": "#E5E7EB",
    "Info gevraagd": "#DBEAFE",
    "Plaatsbezoek gepland": "#C7D2FE",
    "Verslag maken": "#FEF3C7",
    "Offerte maken": "#FDE68A",
    "Offerte verstuurd": "#DDD6FE",
    "Gewonnen": "#BBF7D0",
    "Verloren": "#FEE2E2",
    "No-go": "#E5E7EB",
    "Open": "#FEF3C7",
    "Gedaan": "#BBF7D0",
    "Uitgesteld": "#DBEAFE",
    "Geannuleerd": "#FEE2E2",
}
