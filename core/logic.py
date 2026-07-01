"""Business-logica: opvolgstatus, id-generatie, waardeberekening."""
import uuid
from datetime import date, timedelta

from .config import AFGEHANDELD


def new_id():
    return uuid.uuid4().hex[:8]


def opvolg(row, today=None):
    """Bepaalt de opvolgstatus van een lead."""
    today = today or date.today()
    if row["status"] in AFGEHANDELD:
        return "—"
    d = row["datum_actie"]
    if not isinstance(d, date):
        return "Geen datum"
    if d < today:
        return "\u26a0 Te laat"
    if d <= today + timedelta(days=7):
        return "Deze week"
    return "Later"


def deal_value(panelen, prijs_per_paneel):
    try:
        return int(panelen) * float(prijs_per_paneel)
    except (TypeError, ValueError):
        return 0.0


def offerte_tekst(row, prijs_per_paneel):
    """Genereert een kopieerbare offerte-schatting op basis van de leaddata."""
    panelen = int(row.get("aantal_panelen") or 0)
    waarde = deal_value(panelen, prijs_per_paneel)
    return (
        f"Offerte-schatting — {row.get('bedrijf', '')}\n"
        f"Contact: {row.get('contactpersoon', '')} ({row.get('email', '')})\n"
        f"Locatie: {row.get('regio', '')}\n"
        f"Aantal panelen: {panelen}\n"
        f"Richtprijs: EUR {prijs_per_paneel:.2f}/paneel\n"
        f"Geschatte waarde: EUR {waarde:,.0f}\n"
        f"(Indicatief — definitieve offerte via de offerte-tool.)"
    )
