"""Solvigo — Lead opvolging. Professionele Streamlit-layout."""
import html
import io
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from core import sheets
from core.config import (
    ACTIEF,
    AFGEHANDELD,
    LABELS,
    LEAD_HEADERS,
    SOORTEN,
    STATUSES,
    STATUS_KLEUR,
    TYPES,
)
from core.logic import deal_value, new_id, offerte_tekst, opvolg

st.set_page_config(page_title="Solvigo — Lead opvolging", page_icon="🌞", layout="wide")


# ---------------------------------------------------------------- styling
SOLVIGO_CSS = """
<style>
    :root {
        --solvigo-ink: #10231f;
        --solvigo-muted: #64748b;
        --solvigo-bg: #f4f7f5;
        --solvigo-card: #ffffff;
        --solvigo-line: #dbe5df;
        --solvigo-green: #0f766e;
        --solvigo-green-soft: #e7f5f1;
        --solvigo-gold: #f2b84b;
        --solvigo-danger: #b42318;
    }

    .stApp {
        background: linear-gradient(180deg, #f6faf7 0%, #eef5f1 100%);
    }

    [data-testid="stHeader"] {
        background: rgba(246, 250, 247, 0.72);
        backdrop-filter: blur(10px);
    }

    [data-testid="stSidebar"] {
        background: #eef5f1;
        border-right: 1px solid var(--solvigo-line);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label {
        color: var(--solvigo-ink);
    }

    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 4rem;
        max-width: 1380px;
    }

    h1, h2, h3 {
        color: var(--solvigo-ink);
        letter-spacing: -0.035em;
    }

    div[data-testid="stMetric"] {
        background: var(--solvigo-card);
        border: 1px solid var(--solvigo-line);
        border-radius: 18px;
        padding: 1.0rem 1.05rem;
        box-shadow: 0 10px 30px rgba(15, 34, 31, 0.06);
    }

    div[data-testid="stMetric"] label {
        color: var(--solvigo-muted) !important;
        font-size: 0.86rem !important;
    }

    div[data-testid="stMetricValue"] {
        color: var(--solvigo-ink) !important;
        font-weight: 800;
    }

    .hero {
        background:
            radial-gradient(circle at 95% 18%, rgba(242, 184, 75, 0.28), transparent 28%),
            linear-gradient(135deg, #0f766e 0%, #12352f 100%);
        color: white;
        border-radius: 28px;
        padding: 2.0rem 2.2rem;
        margin-bottom: 1.4rem;
        box-shadow: 0 18px 45px rgba(15, 118, 110, 0.22);
        display: flex;
        justify-content: space-between;
        gap: 1.8rem;
        align-items: stretch;
    }

    .hero h1 {
        color: white;
        font-size: 2.6rem;
        line-height: 1.05;
        margin: 0.15rem 0 0.55rem 0;
    }

    .hero p {
        color: rgba(255,255,255,0.82);
        margin: 0;
        font-size: 1.02rem;
        max-width: 760px;
    }

    .eyebrow {
        color: #f5d58b !important;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        font-size: 0.76rem !important;
        font-weight: 800;
        margin-bottom: 0.35rem !important;
    }

    .hero-panel {
        min-width: 245px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.22);
        border-radius: 22px;
        padding: 1.1rem;
    }

    .hero-panel .small {
        color: rgba(255,255,255,0.72);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        font-weight: 800;
    }

    .hero-panel .big {
        color: white;
        font-size: 2.0rem;
        font-weight: 850;
        margin-top: 0.2rem;
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 1.2rem 0 0.8rem 0;
    }

    .section-title h2, .section-title h3 {
        margin: 0;
    }

    .soft-card {
        background: var(--solvigo-card);
        border: 1px solid var(--solvigo-line);
        border-radius: 20px;
        padding: 1.05rem 1.15rem;
        box-shadow: 0 12px 32px rgba(15, 34, 31, 0.055);
        margin-bottom: 0.85rem;
    }

    .brand-card {
        background: linear-gradient(145deg, #ffffff, #e8f3ee);
        border: 1px solid var(--solvigo-line);
        border-radius: 22px;
        padding: 1.15rem 1.0rem;
        margin-bottom: 1.0rem;
        box-shadow: 0 10px 24px rgba(15, 34, 31, 0.05);
    }

    .brand-logo {
        font-size: 1.55rem;
        font-weight: 850;
        color: var(--solvigo-ink);
        letter-spacing: -0.04em;
        margin-bottom: 0.15rem;
    }

    .brand-sub {
        color: var(--solvigo-muted);
        font-size: 0.86rem;
    }

    .side-note {
        background: rgba(15, 118, 110, 0.08);
        border: 1px solid rgba(15, 118, 110, 0.18);
        border-radius: 16px;
        padding: 0.9rem;
        color: var(--solvigo-ink);
        font-size: 0.88rem;
        margin-top: 1rem;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.26rem 0.62rem;
        font-size: 0.78rem;
        font-weight: 800;
        color: #12352f;
        border: 1px solid rgba(16, 35, 31, 0.08);
        white-space: nowrap;
    }

    .lead-card {
        background: var(--solvigo-card);
        border: 1px solid var(--solvigo-line);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 10px 24px rgba(15, 34, 31, 0.05);
        margin-bottom: 0.75rem;
    }

    .lead-title {
        font-size: 1.05rem;
        font-weight: 850;
        color: var(--solvigo-ink);
        margin-bottom: 0.25rem;
    }

    .lead-meta {
        color: var(--solvigo-muted);
        font-size: 0.88rem;
        line-height: 1.4;
        margin-top: 0.35rem;
    }

    .empty-state {
        background: #ffffff;
        border: 1px dashed #c9d8d0;
        border-radius: 24px;
        padding: 2.0rem;
        text-align: center;
        color: var(--solvigo-ink);
        margin-top: 1rem;
    }

    .empty-state h3 {
        margin-bottom: 0.35rem;
    }

    .alert-card {
        background: #fff7ed;
        border: 1px solid #fed7aa;
        color: #7c2d12;
        border-radius: 20px;
        padding: 1.2rem 1.35rem;
        margin: 1.25rem 0;
    }

    .success-card {
        background: #ecfdf5;
        border: 1px solid #bbf7d0;
        color: #064e3b;
        border-radius: 20px;
        padding: 1.2rem 1.35rem;
        margin: 1.25rem 0;
    }

    .pipeline-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 0.8rem;
        margin: 0.4rem 0 1.25rem 0;
    }

    .pipeline-item {
        background: #ffffff;
        border: 1px solid var(--solvigo-line);
        border-radius: 18px;
        padding: 0.95rem;
        box-shadow: 0 8px 22px rgba(15, 34, 31, 0.045);
    }

    .pipeline-item .label {
        color: var(--solvigo-muted);
        font-size: 0.78rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .pipeline-item .value {
        color: var(--solvigo-ink);
        font-size: 1.75rem;
        font-weight: 850;
        margin-top: 0.2rem;
    }

    .compact-caption {
        color: var(--solvigo-muted);
        font-size: 0.9rem;
        margin-top: -0.25rem;
        margin-bottom: 0.85rem;
    }

    div[data-testid="stTabs"] button {
        border-radius: 999px;
        padding: 0.35rem 0.85rem;
    }

    div[data-testid="stTabs"] [aria-selected="true"] {
        background: var(--solvigo-green-soft);
        color: var(--solvigo-green);
        font-weight: 800;
    }
</style>
"""

st.markdown(SOLVIGO_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- helpers
def esc(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return html.escape(str(value))


def euro(value):
    return f"€ {value:,.0f}".replace(",", ".")


def whole(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except (TypeError, ValueError):
        return "0"


def date_label(value):
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    return "Geen datum"


def status_pill(status):
    kleur = STATUS_KLEUR.get(str(status), "#E5E7EB")
    return f'<span class="status-pill" style="background:{kleur};">{esc(status)}</span>'


def section(title, subtitle=None):
    st.markdown(f'<div class="section-title"><h2>{esc(title)}</h2></div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="compact-caption">{esc(subtitle)}</div>', unsafe_allow_html=True)


def render_lead_card(row, prijs_per_paneel):
    bedrijf = esc(row.get("bedrijf") or "Naamloze lead")
    contact = esc(row.get("contactpersoon") or "Geen contactpersoon")
    regio = esc(row.get("regio") or "Geen regio")
    actie = esc(row.get("volgende_actie") or "Geen volgende actie")
    datum = date_label(row.get("datum_actie"))
    tel = esc(row.get("telefoon") or "Geen telefoon")
    mail = esc(row.get("email") or "Geen e-mail")
    waarde = euro(deal_value(row.get("aantal_panelen", 0), prijs_per_paneel))
    st.markdown(
        f"""
        <div class="lead-card">
            <div style="display:flex; justify-content:space-between; gap:1rem; align-items:flex-start;">
                <div>
                    <div class="lead-title">{bedrijf}</div>
                    <div>{status_pill(row.get('status', ''))}</div>
                </div>
                <div style="font-weight:850; color:#0f766e; white-space:nowrap;">{waarde}</div>
            </div>
            <div class="lead-meta">
                <strong>{contact}</strong> · {regio}<br>
                {tel} · {mail}<br>
                <strong>Actie:</strong> {actie} · <strong>{datum}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def col_config():
    cfg = {
        "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        "type": st.column_config.SelectboxColumn("Type", options=TYPES, width="medium"),
        "status": st.column_config.SelectboxColumn("Status", options=STATUSES, width="medium"),
        "aantal_panelen": st.column_config.NumberColumn("# Panelen", min_value=0, step=50),
        "eerste_contact": st.column_config.DateColumn("1e contact", format="DD/MM/YYYY"),
        "laatste_contact": st.column_config.DateColumn("Laatste contact", format="DD/MM/YYYY"),
        "datum_actie": st.column_config.DateColumn("Datum actie", format="DD/MM/YYYY"),
        "email": st.column_config.TextColumn("E-mail", width="medium"),
        "notities": st.column_config.TextColumn("Notities", width="large"),
    }
    for c in ["bedrijf", "contactpersoon", "functie", "telefoon", "regio", "bron", "volgende_actie"]:
        cfg[c] = st.column_config.TextColumn(LABELS[c])
    return cfg


def to_excel_bytes(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        df.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Leads")
    return buf.getvalue()


def seed_examples():
    today_seed = date.today()
    rows = [
        dict(id=new_id(), bedrijf="Kempen Solar bvba", type="Installateur",
             contactpersoon="Tom Peeters", functie="Zaakvoerder",
             email="info@kempensolar.be", telefoon="014 12 34 56", regio="Herentals",
             aantal_panelen=0, bron="Google Maps", status="Gecontacteerd",
             eerste_contact=today_seed - timedelta(days=8), laatste_contact=today_seed - timedelta(days=8),
             volgende_actie="Bellen voor afspraak", datum_actie=today_seed - timedelta(days=1),
             notities="1e mail gestuurd, nog geen reactie."),
        dict(id=new_id(), bedrijf="BioEnergie Geel NV", type="Eindklant industrieel",
             contactpersoon="Sofie Janssens", functie="Facility manager",
             email="s.janssens@bioenergiegeel.be", telefoon="014 98 76 54", regio="Geel",
             aantal_panelen=4200, bron="LinkedIn", status="Interesse / gesprek",
             eerste_contact=today_seed - timedelta(days=14), laatste_contact=today_seed - timedelta(days=3),
             volgende_actie="Offerte opmaken", datum_actie=today_seed + timedelta(days=2),
             notities="Biogassite. Interesse in jaarcontract."),
        dict(id=new_id(), bedrijf="Zonnedak O&M", type="O&M",
             contactpersoon="Bart Willems", functie="Operations",
             email="bart@zonnedak.be", telefoon="03 456 78 90", regio="Antwerpen",
             aantal_panelen=1500, bron="Beurs", status="Offerte verstuurd",
             eerste_contact=today_seed - timedelta(days=21), laatste_contact=today_seed - timedelta(days=5),
             volgende_actie="Opvolgen offerte", datum_actie=today_seed + timedelta(days=4),
             notities="Offerte 1.500 panelen verstuurd. Vraagt referenties."),
    ]
    sheets.save_leads(pd.DataFrame(rows).reindex(columns=LEAD_HEADERS))


# ---------------------------------------------------------------- sidebar
st.sidebar.markdown(
    """
    <div class="brand-card">
        <div class="brand-logo">🌞 Solvigo</div>
        <div class="brand-sub">Leadopvolging voor zonnepaneelreiniging</div>
    </div>
    """,
    unsafe_allow_html=True,
)
prijs = st.sidebar.number_input(
    "Richtprijs per paneel (€)",
    min_value=0.0,
    value=st.session_state.get("prijs", 1.50),
    step=0.10,
)
st.session_state["prijs"] = prijs
if st.sidebar.button("🔄 Data vernieuwen", use_container_width=True):
    sheets.load_leads.clear()
    sheets.load_log.clear()
    st.rerun()

st.sidebar.markdown(
    """
    <div class="side-note">
        <strong>Workflow</strong><br>
        Dashboard bekijken → opvolging afwerken → leadfiche bijwerken → offertebrug gebruiken.
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- laden
try:
    df = sheets.load_leads()
    log = sheets.load_log()
except KeyError:
    st.markdown(
        """
        <div class="hero">
            <div>
                <p class="eyebrow">Configuratie nodig</p>
                <h1>Solvigo Leadtracker</h1>
                <p>De app is gedeployed. Alleen de Streamlit Secrets ontbreken nog.</p>
            </div>
            <div class="hero-panel">
                <div class="small">Status</div>
                <div class="big">Secrets</div>
            </div>
        </div>
        <div class="alert-card">
            <strong>Secrets ontbreken.</strong><br>
            Zet <code>[sheet].id</code> en <code>[gcp_service_account]</code> in je Streamlit Secrets.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()
except Exception as e:
    st.markdown(
        f"""
        <div class="alert-card">
            <strong>Google Sheet kan niet geladen worden.</strong><br>
            Foutmelding: {esc(e)}<br><br>
            Controleer of de Sheet gedeeld is met het service-account als <strong>Bewerker</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

today = date.today()
if len(df):
    df["_opvolg"] = df.apply(lambda r: opvolg(r, today), axis=1)
else:
    df["_opvolg"] = pd.Series(dtype=str)

actief = df[~df["status"].isin(AFGEHANDELD)] if len(df) else df
gewonnen = int((df["status"] == "Gewonnen").sum()) if len(df) else 0
verloren = int((df["status"] == "Verloren").sum()) if len(df) else 0
conv = gewonnen / (gewonnen + verloren) if (gewonnen + verloren) else 0
pijplijn_waarde = deal_value(actief["aantal_panelen"].sum(), prijs) if len(actief) else 0
te_laat = df[df["_opvolg"] == "⚠ Te laat"].sort_values("datum_actie") if len(df) else df
week = df[df["_opvolg"] == "Deze week"].sort_values("datum_actie") if len(df) else df

st.markdown(
    f"""
    <div class="hero">
        <div>
            <p class="eyebrow">Solvigo CRM</p>
            <h1>Lead opvolging</h1>
            <p>Een duidelijk overzicht van prospects, opvolgacties, offertes en potentiële omzet.</p>
        </div>
        <div class="hero-panel">
            <div class="small">Actieve pijplijn</div>
            <div class="big">{euro(pijplijn_waarde)}</div>
            <div style="color:rgba(255,255,255,0.72); font-size:0.9rem;">{whole(len(actief))} actieve leads</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if df.empty:
    st.markdown(
        """
        <div class="empty-state">
            <h3>Nog geen leads</h3>
            <p>Start met een nieuwe lead of laad voorbeelddata om de layout te testen.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Voorbeelddata laden", type="primary"):
        seed_examples()
        st.rerun()

tabs = st.tabs(["📊 Dashboard", "🔔 Opvolgen", "📋 Leads", "👤 Leadfiche", "➕ Nieuwe lead"])

# ================================================================ DASHBOARD
with tabs[0]:
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Totaal leads", whole(len(df)))
    k2.metric("Actief", whole(len(actief)))
    k3.metric("Te laat", whole(len(te_laat)))
    k4.metric("Conversie", f"{conv:.0%}")
    k5.metric("Pijplijnwaarde", euro(pijplijn_waarde))

    section("Pipeline", "Aantal leads per fase. Zo zie je meteen waar werk blijft hangen.")
    counts = df["status"].value_counts().reindex(STATUSES).fillna(0).astype(int) if len(df) else pd.Series(0, index=STATUSES)
    items = "".join(
        f"""
        <div class="pipeline-item">
            <div class="label">{esc(status)}</div>
            <div class="value">{int(count)}</div>
        </div>
        """
        for status, count in counts.items()
    )
    st.markdown(f'<div class="pipeline-grid">{items}</div>', unsafe_allow_html=True)

    d1, d2 = st.columns([1.15, 1])
    with d1:
        section("Eerst opvolgen")
        urgent = pd.concat([te_laat, week]).drop_duplicates(subset=["id"]).head(5) if len(df) else df
        if len(urgent):
            for _, r in urgent.iterrows():
                render_lead_card(r, prijs)
        else:
            st.markdown('<div class="success-card"><strong>Geen dringende opvolging.</strong><br>Je pipeline is op dit moment rustig.</div>', unsafe_allow_html=True)
    with d2:
        section("Panelen per actieve fase")
        perfase = actief.groupby("status")["aantal_panelen"].sum().reindex(ACTIEF).fillna(0).astype(int) if len(actief) else pd.Series(0, index=ACTIEF)
        st.bar_chart(perfase)

# ================================================================ OPVOLGEN
with tabs[1]:
    geen = df[df["_opvolg"] == "Geen datum"].sort_values("bedrijf") if len(df) else df
    c1, c2, c3 = st.columns(3)
    c1.metric("⚠ Te laat", len(te_laat))
    c2.metric("Deze week", len(week))
    c3.metric("Zonder datum", len(geen))

    cols = ["bedrijf", "contactpersoon", "telefoon", "email", "status", "volgende_actie", "datum_actie", "notities"]

    section("⚠ Te laat", "Deze leads eerst aanpakken.")
    if len(te_laat):
        st.dataframe(te_laat[cols].rename(columns=LABELS), hide_index=True, use_container_width=True)
    else:
        st.markdown('<div class="success-card"><strong>Niets te laat.</strong><br>Alle opvolgingen zijn onder controle.</div>', unsafe_allow_html=True)

    section("Deze week")
    if len(week):
        st.dataframe(week[cols].rename(columns=LABELS), hide_index=True, use_container_width=True)
    else:
        st.info("Geen acties gepland deze week.")

    if len(geen):
        with st.expander(f"Zonder opvolgdatum ({len(geen)})"):
            st.dataframe(geen[cols].rename(columns=LABELS), hide_index=True, use_container_width=True)

# ================================================================ ALLE LEADS
with tabs[2]:
    section("Alle leads", "Filter, bewerk en exporteer je volledige leadlijst.")
    f1, f2, f3 = st.columns([2, 2, 3])
    f_status = f1.multiselect("Status", STATUSES)
    f_type = f2.multiselect("Type", TYPES)
    zoek = f3.text_input("Zoek op bedrijf of contact")

    view = df.drop(columns=["_opvolg"]).copy()
    if f_status:
        view = view[view["status"].isin(f_status)]
    if f_type:
        view = view[view["type"].isin(f_type)]
    if zoek:
        m = (view["bedrijf"].str.contains(zoek, case=False, na=False) |
             view["contactpersoon"].str.contains(zoek, case=False, na=False))
        view = view[m]

    edited = st.data_editor(
        view,
        column_config=col_config(),
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor",
    )

    a, b, c = st.columns([1.1, 1.1, 4])
    if a.button("💾 Opslaan", type="primary", use_container_width=True):
        edited = edited.copy()
        edited["id"] = edited["id"].apply(lambda x: x if str(x).strip() else new_id())
        base = df.drop(columns=["_opvolg"]).set_index("id")
        base.update(edited.set_index("id"))
        base = base.reset_index()
        nieuw = edited[~edited["id"].isin(df["id"])]
        if len(nieuw):
            base = pd.concat([base, nieuw], ignore_index=True)
        sheets.save_leads(base)
        st.success("Opgeslagen.")
        st.rerun()
    if b.button("🔄 Vernieuwen", use_container_width=True):
        sheets.load_leads.clear()
        st.rerun()
    c.download_button(
        "⬇ Exporteer naar Excel",
        to_excel_bytes(df.drop(columns=["_opvolg"])),
        file_name="solvigo_leads.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

# ================================================================ LEAD DETAIL
with tabs[3]:
    if df.empty:
        st.info("Nog geen leads.")
    else:
        section("Leadfiche", "Detailweergave met opvolging, logboek en offertebrug.")
        keuze = st.selectbox(
            "Kies een lead",
            df["id"].tolist(),
            format_func=lambda i: df.loc[df["id"] == i, "bedrijf"].iloc[0] or "(naamloos)",
        )
        row = df[df["id"] == keuze].iloc[0].to_dict()

        left, right = st.columns([3, 1.35])

        with left:
            st.markdown(f"### {esc(row['bedrijf'] or '(naamloos)')}", unsafe_allow_html=True)
            with st.form("edit_lead"):
                g1, g2 = st.columns(2)
                bedrijf = g1.text_input("Bedrijf", row["bedrijf"])
                typ = g2.selectbox("Type", TYPES, index=TYPES.index(row["type"]) if row["type"] in TYPES else 0)
                contact = g1.text_input("Contact", row["contactpersoon"])
                functie = g2.text_input("Functie", row["functie"])
                email = g1.text_input("E-mail", row["email"])
                tel = g2.text_input("Telefoon", row["telefoon"])
                regio = g1.text_input("Regio", row["regio"])
                panelen = g2.number_input("Aantal panelen", min_value=0, step=50, value=int(row["aantal_panelen"] or 0))
                bron = g1.text_input("Bron", row["bron"])
                status = g2.selectbox("Status", STATUSES, index=STATUSES.index(row["status"]) if row["status"] in STATUSES else 0)
                actie = g1.text_input("Volgende actie", row["volgende_actie"])
                d_actie = g2.date_input("Datum actie", value=row["datum_actie"] if isinstance(row["datum_actie"], date) else today)
                notities = st.text_area("Notities", row["notities"])
                if st.form_submit_button("💾 Wijzigingen opslaan", type="primary"):
                    full = df.drop(columns=["_opvolg"]).copy()
                    idx = full.index[full["id"] == keuze][0]
                    full.loc[idx, ["bedrijf", "type", "contactpersoon", "functie", "email", "telefoon", "regio", "aantal_panelen", "bron", "status", "volgende_actie", "datum_actie", "notities"]] = [
                        bedrijf, typ, contact, functie, email, tel, regio, panelen, bron, status, actie, d_actie, notities]
                    sheets.save_leads(full)
                    st.success("Opgeslagen.")
                    st.rerun()

            with st.expander("🗑 Lead verwijderen"):
                st.warning("Dit verwijdert de lead en zijn logboek.")
                if st.button("Definitief verwijderen"):
                    sheets.save_leads(df.drop(columns=["_opvolg"])[df["id"] != keuze])
                    if len(log):
                        sheets.save_log(log[log["lead_id"] != keuze])
                    st.rerun()

        with right:
            waarde = deal_value(row["aantal_panelen"], prijs)
            st.metric("Geschatte waarde", euro(waarde))
            st.caption(f"{int(row['aantal_panelen'] or 0)} panelen × € {prijs:.2f}")
            st.markdown(status_pill(row["status"]), unsafe_allow_html=True)
            st.markdown("#### ➡ Offertebrug")
            st.text_area("Kopieer naar je offerte-tool", offerte_tekst(row, prijs), height=205)

        st.divider()
        st.markdown("### 📞 Contactmoment loggen")
        with st.form("log_form", clear_on_submit=True):
            l1, l2 = st.columns([1, 3])
            soort = l1.selectbox("Soort", SOORTEN)
            notitie = l2.text_input("Notitie")
            n1, n2 = st.columns(2)
            zet_actie = n1.text_input("Nieuwe volgende actie (optioneel)")
            zet_datum = n2.date_input("Nieuwe datum actie", value=today + timedelta(days=7))
            if st.form_submit_button("➕ Loggen"):
                sheets.append_log(dict(id=new_id(), lead_id=keuze, datum=today, soort=soort, notitie=notitie))
                full = df.drop(columns=["_opvolg"]).copy()
                idx = full.index[full["id"] == keuze][0]
                full.loc[idx, "laatste_contact"] = today
                if row["status"] == "Nieuw":
                    full.loc[idx, "status"] = "Gecontacteerd"
                    if not isinstance(row["eerste_contact"], date):
                        full.loc[idx, "eerste_contact"] = today
                if zet_actie.strip():
                    full.loc[idx, "volgende_actie"] = zet_actie
                    full.loc[idx, "datum_actie"] = zet_datum
                sheets.save_leads(full)
                st.rerun()

        hist = log[log["lead_id"] == keuze].sort_values("datum", ascending=False) if len(log) else log
        if len(hist):
            st.markdown("**Historiek**")
            st.dataframe(hist[["datum", "soort", "notitie"]].rename(columns=LABELS), hide_index=True, use_container_width=True)
        else:
            st.caption("Nog geen contactmomenten gelogd.")

# ================================================================ NIEUWE LEAD
with tabs[4]:
    section("Nieuwe lead", "Snel één lead toevoegen, bijvoorbeeld na Google Maps, LinkedIn of een telefoongesprek.")
    with st.form("nieuw", clear_on_submit=True):
        c1, c2 = st.columns(2)
        bedrijf = c1.text_input("Bedrijf *")
        typ = c2.selectbox("Type", TYPES)
        contact = c1.text_input("Contactpersoon")
        functie = c2.text_input("Functie")
        email = c1.text_input("E-mail")
        tel = c2.text_input("Telefoon")
        regio = c1.text_input("Regio")
        panelen = c2.number_input("Aantal panelen (schatting)", min_value=0, step=50)
        bron = c1.text_input("Bron")
        status = c2.selectbox("Status", STATUSES)
        actie = c1.text_input("Volgende actie", value="1e mail sturen")
        d_actie = c2.date_input("Datum volgende actie", value=today + timedelta(days=2))
        notities = st.text_area("Notities")
        ok = st.form_submit_button("➕ Toevoegen", type="primary")
    if ok:
        if not bedrijf.strip():
            st.warning("Vul minstens een bedrijfsnaam in.")
        else:
            gecontacteerd = status != "Nieuw"
            sheets.append_lead(dict(
                id=new_id(), bedrijf=bedrijf, type=typ, contactpersoon=contact,
                functie=functie, email=email, telefoon=tel, regio=regio,
                aantal_panelen=panelen, bron=bron, status=status,
                eerste_contact=today if gecontacteerd else "",
                laatste_contact=today if gecontacteerd else "",
                volgende_actie=actie, datum_actie=d_actie, notities=notities,
            ))
            st.success(f"'{bedrijf}' toegevoegd.")
            st.rerun()
