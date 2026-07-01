"""Business-logica voor partners, projecten, acties en bezoeken."""
import uuid
from datetime import date, timedelta

from .config import CADANS, PARTNER_AFGEHANDELD, PROJECT_AFGEHANDELD


def new_id(prefix=""):
    base = uuid.uuid4().hex[:8]
    return f"{prefix}{base}" if prefix else base


def euro(value):
    try:
        return f"€ {float(value):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return "€ 0"


def whole(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def deal_value(panelen, prijs_per_paneel):
    try:
        return int(panelen) * float(prijs_per_paneel)
    except (TypeError, ValueError):
        return 0.0


def project_value(row, prijs_per_paneel):
    """Gebruik ingevulde verwachte waarde, anders panelen x richtprijs."""
    try:
        ingevuld = float(row.get("verwachte_waarde") or 0)
    except (TypeError, ValueError):
        ingevuld = 0
    if ingevuld > 0:
        return ingevuld
    return deal_value(row.get("aantal_panelen", 0), prijs_per_paneel)


def opvolg_status(status, datum_actie, afgehandeld, today=None):
    today = today or date.today()
    if status in afgehandeld:
        return "—"
    if not isinstance(datum_actie, date):
        return "Geen datum"
    if datum_actie < today:
        return "Te laat"
    if datum_actie == today:
        return "Vandaag"
    if datum_actie <= today + timedelta(days=7):
        return "Deze week"
    return "Later"


def action_bucket(row, today=None):
    today = today or date.today()
    if row.get("status") != "Open":
        return "Afgehandeld"
    d = row.get("datum_actie")
    if not isinstance(d, date):
        return "Geen datum"
    if d < today:
        return "Te laat"
    if d == today:
        return "Vandaag"
    if d <= today + timedelta(days=7):
        return "Deze week"
    return "Later"


def partner_is_active(row):
    return row.get("status") not in PARTNER_AFGEHANDELD


def project_is_active(row):
    return row.get("status") not in PROJECT_AFGEHANDELD


def cadans_namen():
    return list(CADANS.keys())


def cadans_stappen(naam):
    return CADANS.get(naam, [])


def cadans_actie_dict(relatie_type, relatie_id, relatie_naam, cadans, stap_index,
                      basisdatum, today=None):
    """Bouwt de actie-dict voor een cadansstap. basisdatum = datum waarop de vorige
    stap is afgerond (of de startdatum voor stap 0)."""
    today = today or date.today()
    stappen = cadans_stappen(cadans)
    if stap_index >= len(stappen):
        return None
    stap = stappen[stap_index]
    datum = basisdatum + timedelta(days=int(stap.get("wacht", 0)))
    totaal = len(stappen)
    return dict(
        id=new_id("A"),
        relatie_type=relatie_type,
        relatie_id=relatie_id,
        relatie_naam=relatie_naam,
        actie=stap["label"],
        datum_actie=datum,
        prioriteit="Normaal",
        status="Open",
        kanaal=stap.get("kanaal", "Andere"),
        notities=f"Cadans '{cadans}' — stap {stap_index + 1}/{totaal}",
        aangemaakt_op=today,
        afgerond_op="",
        cadans=cadans,
        cadans_stap=str(stap_index),
    )


def cadans_volgende(row, today=None):
    """Geeft de dict voor de volgende cadansstap na het afronden van 'row', of None."""
    today = today or date.today()
    cad = str(row.get("cadans") or "").strip()
    if not cad:
        return None
    try:
        stap = int(row.get("cadans_stap") or 0)
    except (TypeError, ValueError):
        stap = 0
    if stap + 1 >= len(cadans_stappen(cad)):
        return None
    return cadans_actie_dict(
        row.get("relatie_type", ""), row.get("relatie_id", ""), row.get("relatie_naam", ""),
        cad, stap + 1, today, today)


def offerte_tekst_project(row, prijs_per_paneel):
    panelen = int(row.get("aantal_panelen") or 0)
    waarde = project_value(row, prijs_per_paneel)
    partner = row.get("partner_bedrijf") or "Geen partner"
    return (
        f"Offerte-info — {row.get('projectnaam', '')}\n"
        f"Klant: {row.get('klant_bedrijf', '')}\n"
        f"Contact: {row.get('contactpersoon', '')} ({row.get('email', '')})\n"
        f"Telefoon: {row.get('telefoon', '')}\n"
        f"Adres/regio: {row.get('adres', '')} — {row.get('regio', '')}\n"
        f"Aantal panelen: {panelen}\n"
        f"Bron: {row.get('bron_type', '')}\n"
        f"Partner/installateur: {partner}\n"
        f"Richtprijs: EUR {prijs_per_paneel:.2f}/paneel\n"
        f"Geschatte waarde: EUR {waarde:,.0f}\n"
        f"Notities: {row.get('notities', '')}\n"
        f"(Indicatief — definitieve offerte via de offerte-tool.)"
    )
