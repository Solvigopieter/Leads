"""Solvigo CRM — partners, projecten, actieblad en plaatsbezoeken."""
import html
import io
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from core import sheets
from core.config import (
    ACTION_CHANNELS,
    ACTION_HEADERS,
    ACTION_PRIORITIES,
    ACTION_STATUSES,
    BRON_TYPES,
    LABELS,
    LEGACY_PARTNER_TYPES,
    LOG_HEADERS,
    LOG_SOORTEN,
    PARTNER_HEADERS,
    PARTNER_STATUSES,
    PARTNER_TYPES,
    PROJECT_AFGEHANDELD,
    PROJECT_HEADERS,
    PROJECT_STATUSES,
    STATUS_KLEUR,
    VISIT_DAK_TYPES,
    VISIT_HEADERS,
    VISIT_TOEGANG,
    VISIT_VERVUILING,
)
from core.logic import (
    action_bucket,
    cadans_actie_dict,
    cadans_namen,
    cadans_stappen,
    cadans_volgende,
    deal_value,
    euro,
    new_id,
    offerte_tekst_project,
    project_value,
    whole,
)

st.set_page_config(page_title="Solvigo CRM", page_icon="🌞", layout="wide")

CSS = """
<style>
:root {
    --ink: #10231f;
    --muted: #64748b;
    --line: #dbe5df;
    --bg: #f4f7f5;
    --card: #ffffff;
    --green: #0f766e;
    --green-dark: #12352f;
    --green-soft: #e7f5f1;
    --gold: #f2b84b;
    --danger: #b42318;
}
.stApp { background: linear-gradient(180deg, #f7fbf8 0%, #eef5f1 100%); }
[data-testid="stHeader"] { background: rgba(246,250,247,.75); backdrop-filter: blur(10px); }
[data-testid="stSidebar"] { background: #edf5f0; border-right: 1px solid var(--line); }
.block-container { padding-top: 2rem; max-width: 1440px; }
h1,h2,h3 { color: var(--ink); letter-spacing: -0.035em; }
div[data-testid="stMetric"] { background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 1rem; box-shadow: 0 10px 28px rgba(15,34,31,.055); }
div[data-testid="stMetricValue"] { color: var(--ink); font-weight: 850; }
div[data-testid="stMetric"] label { color: var(--muted) !important; }
.hero { background: radial-gradient(circle at 95% 18%, rgba(242,184,75,.30), transparent 27%), linear-gradient(135deg, #0f766e 0%, #12352f 100%); color: white; border-radius: 28px; padding: 2rem 2.2rem; margin-bottom: 1.3rem; display: flex; justify-content: space-between; gap: 1.5rem; box-shadow: 0 18px 45px rgba(15,118,110,.22); }
.hero h1 { color: white; font-size: 2.55rem; line-height: 1.05; margin: .1rem 0 .55rem 0; }
.hero p { color: rgba(255,255,255,.82); margin: 0; max-width: 820px; }
.eyebrow { color: #f8d78b !important; text-transform: uppercase; letter-spacing: .16em; font-size: .75rem !important; font-weight: 850; margin-bottom: .35rem !important; }
.hero-panel { min-width: 260px; background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22); border-radius: 22px; padding: 1.1rem; }
.hero-panel .small { color: rgba(255,255,255,.72); font-size: .78rem; text-transform: uppercase; letter-spacing: .09em; font-weight: 800; }
.hero-panel .big { color: white; font-size: 2rem; font-weight: 850; margin-top: .2rem; }
.brand-card { background: linear-gradient(145deg,#fff,#e8f3ee); border: 1px solid var(--line); border-radius: 22px; padding: 1.15rem 1rem; margin-bottom: 1rem; box-shadow: 0 10px 24px rgba(15,34,31,.05); }
.brand-logo { font-size: 1.55rem; font-weight: 850; color: var(--ink); letter-spacing: -.04em; }
.brand-sub { color: var(--muted); font-size: .86rem; }
.side-note { background: rgba(15,118,110,.08); border: 1px solid rgba(15,118,110,.18); border-radius: 16px; padding: .9rem; color: var(--ink); font-size: .88rem; margin-top: 1rem; }
.section-title { margin: 1.15rem 0 .65rem 0; }
.section-title h2, .section-title h3 { margin: 0; }
.caption2 { color: var(--muted); font-size: .9rem; margin-top: -.2rem; margin-bottom: .8rem; }
.soft-card { background: #fff; border: 1px solid var(--line); border-radius: 20px; padding: 1.05rem 1.15rem; box-shadow: 0 12px 32px rgba(15,34,31,.055); margin-bottom: .85rem; }
.alert-card { background: #fff7ed; border: 1px solid #fed7aa; color: #7c2d12; border-radius: 20px; padding: 1.2rem 1.35rem; margin: 1.25rem 0; }
.success-card { background: #ecfdf5; border: 1px solid #bbf7d0; color: #064e3b; border-radius: 20px; padding: 1.2rem 1.35rem; margin: 1.25rem 0; }
.empty-state { background: #fff; border: 1px dashed #c9d8d0; border-radius: 24px; padding: 2rem; text-align: center; color: var(--ink); }
.status-pill { display: inline-flex; align-items: center; border-radius: 999px; padding: .26rem .62rem; font-size: .78rem; font-weight: 850; color: #12352f; border: 1px solid rgba(16,35,31,.08); white-space: nowrap; }
.action-card { background: #fff; border: 1px solid var(--line); border-left: 6px solid var(--green); border-radius: 18px; padding: 1rem; box-shadow: 0 10px 24px rgba(15,34,31,.05); margin-bottom: .75rem; }
.action-card.high { border-left-color: #b42318; }
.action-title { font-size: 1.03rem; font-weight: 850; color: var(--ink); }
.action-meta { color: var(--muted); font-size: .88rem; line-height: 1.45; margin-top: .35rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(185px, 1fr)); gap: .8rem; margin: .4rem 0 1.25rem 0; }
.grid-item { background: #fff; border: 1px solid var(--line); border-radius: 18px; padding: .95rem; box-shadow: 0 8px 22px rgba(15,34,31,.045); }
.grid-item .label { color: var(--muted); font-size: .78rem; font-weight: 850; text-transform: uppercase; letter-spacing: .08em; }
.grid-item .value { color: var(--ink); font-size: 1.65rem; font-weight: 850; margin-top: .2rem; }
div[data-testid="stTabs"] button { border-radius: 999px; padding: .35rem .85rem; }
div[data-testid="stTabs"] [aria-selected="true"] { background: var(--green-soft); color: var(--green); font-weight: 850; }
code { color: #0f766e; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------- helpers
def esc(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return html.escape(str(value))


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
        st.markdown(f'<div class="caption2">{esc(subtitle)}</div>', unsafe_allow_html=True)


def relation_options(partners, projects):
    opts = []
    for _, r in partners.sort_values("bedrijf").iterrows():
        name = r.get("bedrijf") or "Naamloze partner"
        opts.append(("Partner", r["id"], name, f"Partner — {name}"))
    for _, r in projects.sort_values("projectnaam").iterrows():
        name = r.get("projectnaam") or r.get("klant_bedrijf") or "Naamloos project"
        opts.append(("Project", r["id"], name, f"Project — {name}"))
    return opts


def partner_select_options(partners):
    opts = [("", "Geen partner/installateur")]
    for _, r in partners.sort_values("bedrijf").iterrows():
        name = r.get("bedrijf") or "Naamloze partner"
        opts.append((r["id"], name))
    return opts


def action_card(row):
    high = " high" if row.get("prioriteit") == "Hoog" else ""
    st.markdown(
        f"""
        <div class="action-card{high}">
          <div style="display:flex; justify-content:space-between; gap:1rem; align-items:flex-start;">
            <div>
              <div class="action-title">{esc(row.get('actie') or 'Actie zonder titel')}</div>
              <div style="margin-top:.25rem;">{status_pill(row.get('status','Open'))}</div>
            </div>
            <div style="font-weight:850; color:#0f766e; white-space:nowrap;">{date_label(row.get('datum_actie'))}</div>
          </div>
          <div class="action-meta">
            <strong>{esc(row.get('relatie_naam'))}</strong> · {esc(row.get('relatie_type'))}<br>
            {esc(row.get('kanaal'))} · Prioriteit: {esc(row.get('prioriteit'))}<br>
            {esc(row.get('notities'))}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def save_filtered_table(original, edited, key_col, save_func, drop_cols=None):
    drop_cols = drop_cols or []
    original_clean = original.drop(columns=[c for c in drop_cols if c in original.columns]).copy()
    edited = edited.drop(columns=[c for c in drop_cols if c in edited.columns]).copy()
    edited[key_col] = edited[key_col].apply(lambda x: x if str(x).strip() else new_id())
    base = original_clean.set_index(key_col)
    base.update(edited.set_index(key_col))
    base = base.reset_index()
    nieuw = edited[~edited[key_col].isin(original_clean[key_col])]
    if len(nieuw):
        base = pd.concat([base, nieuw], ignore_index=True)
    save_func(base)


def afrond_actie(actions_df, action_id, today):
    """Zet een actie op 'Gedaan', logt ze, en maakt automatisch de volgende
    cadansstap aan indien van toepassing."""
    df = actions_df.drop(columns=["_bucket"], errors="ignore").copy()
    idx = df.index[df["id"] == action_id]
    if len(idx) == 0:
        return
    i = idx[0]
    df.loc[i, "status"] = "Gedaan"
    df.loc[i, "afgerond_op"] = today
    row = df.loc[i].to_dict()
    volgende = cadans_volgende(row, today)
    sheets.save_actions(df)
    if volgende:
        sheets.append_action(volgende)
    soort = row.get("kanaal") if row.get("kanaal") in LOG_SOORTEN else "Notitie"
    sheets.append_log(dict(
        id=new_id("L"), relatie_type=row.get("relatie_type", ""),
        relatie_id=row.get("relatie_id", ""), relatie_naam=row.get("relatie_naam", ""),
        datum=today, soort=soort, notitie=f"Afgerond: {row.get('actie', '')}"))
    return volgende


def snooze_actie(actions_df, action_id, dagen, today):
    df = actions_df.drop(columns=["_bucket"], errors="ignore").copy()
    idx = df.index[df["id"] == action_id]
    if len(idx) == 0:
        return
    i = idx[0]
    huidig = df.loc[i, "datum_actie"]
    basis = huidig if isinstance(huidig, date) and huidig > today else today
    df.loc[i, "datum_actie"] = basis + timedelta(days=dagen)
    sheets.save_actions(df)


def agenda_actie_kaart(row, actions_df, today):
    """Actiekaart met afrond- en uitstelknoppen (voor de agenda)."""
    high = " high" if row.get("prioriteit") == "Hoog" else ""
    cad = str(row.get("cadans") or "").strip()
    cad_line = ""
    if cad:
        stappen = cadans_stappen(cad)
        try:
            stap = int(row.get("cadans_stap") or 0) + 1
        except (TypeError, ValueError):
            stap = 1
        cad_line = f'<br>🔁 <strong>{esc(cad)}</strong> · stap {stap}/{len(stappen)}'
    st.markdown(
        f"""
        <div class="action-card{high}">
          <div style="display:flex; justify-content:space-between; gap:1rem; align-items:flex-start;">
            <div>
              <div class="action-title">{esc(row.get('actie') or 'Actie')}</div>
              <div style="margin-top:.25rem;">{status_pill(row.get('status','Open'))}</div>
            </div>
            <div style="font-weight:850; color:#0f766e; white-space:nowrap;">{date_label(row.get('datum_actie'))}</div>
          </div>
          <div class="action-meta">
            <strong>{esc(row.get('relatie_naam'))}</strong> · {esc(row.get('relatie_type'))} · {esc(row.get('kanaal'))}{cad_line}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    b1, b2, b3, _ = st.columns([1.1, 1, 1, 3])
    aid = row["id"]
    if b1.button("✓ Afronden", key=f"done_{aid}", use_container_width=True):
        volgende = afrond_actie(actions_df, aid, today)
        if volgende:
            st.toast(f"Volgende stap ingepland: {volgende['actie']} ({date_label(volgende['datum_actie'])})")
        st.rerun()
    if b2.button("+3d", key=f"sn3_{aid}", use_container_width=True):
        snooze_actie(actions_df, aid, 3, today)
        st.rerun()
    if b3.button("+7d", key=f"sn7_{aid}", use_container_width=True):
        snooze_actie(actions_df, aid, 7, today)
        st.rerun()


def to_excel_bytes(partners, projects, actions, visits, log):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        partners.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Partners")
        projects.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Projecten")
        actions.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Acties")
        visits.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Plaatsbezoeken")
        log.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Log")
    return buf.getvalue()


def project_col_config(partners):
    partner_names = [name for _, name in partner_select_options(partners)]
    return {
        "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        "projectnaam": st.column_config.TextColumn("Project", width="medium"),
        "klant_bedrijf": st.column_config.TextColumn("Klant", width="medium"),
        "contactpersoon": st.column_config.TextColumn("Contact", width="medium"),
        "email": st.column_config.TextColumn("E-mail", width="medium"),
        "telefoon": st.column_config.TextColumn("Telefoon", width="medium"),
        "adres": st.column_config.TextColumn("Adres", width="large"),
        "regio": st.column_config.TextColumn("Regio"),
        "aantal_panelen": st.column_config.NumberColumn("# panelen", min_value=0, step=50),
        "partner_bedrijf": st.column_config.SelectboxColumn("Partner", options=partner_names, width="medium"),
        "bron_type": st.column_config.SelectboxColumn("Bron type", options=BRON_TYPES, width="medium"),
        "status": st.column_config.SelectboxColumn("Status", options=PROJECT_STATUSES, width="medium"),
        "eerste_contact": st.column_config.DateColumn("Eerste contact", format="DD/MM/YYYY"),
        "laatste_contact": st.column_config.DateColumn("Laatste contact", format="DD/MM/YYYY"),
        "datum_actie": st.column_config.DateColumn("Datum actie", format="DD/MM/YYYY"),
        "verwachte_waarde": st.column_config.NumberColumn("Waarde", min_value=0, step=100),
        "notities": st.column_config.TextColumn("Notities", width="large"),
    }


def partner_col_config():
    return {
        "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        "bedrijf": st.column_config.TextColumn("Bedrijf", width="medium"),
        "type": st.column_config.SelectboxColumn("Type", options=PARTNER_TYPES, width="medium"),
        "contactpersoon": st.column_config.TextColumn("Contact", width="medium"),
        "functie": st.column_config.TextColumn("Functie"),
        "email": st.column_config.TextColumn("E-mail", width="medium"),
        "telefoon": st.column_config.TextColumn("Telefoon"),
        "regio": st.column_config.TextColumn("Regio"),
        "website": st.column_config.TextColumn("Website"),
        "status": st.column_config.SelectboxColumn("Status", options=PARTNER_STATUSES, width="medium"),
        "bron": st.column_config.TextColumn("Bron"),
        "eerste_contact": st.column_config.DateColumn("Eerste contact", format="DD/MM/YYYY"),
        "laatste_contact": st.column_config.DateColumn("Laatste contact", format="DD/MM/YYYY"),
        "datum_actie": st.column_config.DateColumn("Datum actie", format="DD/MM/YYYY"),
        "notities": st.column_config.TextColumn("Notities", width="large"),
    }


def action_col_config():
    return {
        "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        "relatie_type": st.column_config.SelectboxColumn("Relatie type", options=["Partner", "Project"], width="small"),
        "relatie_naam": st.column_config.TextColumn("Relatie", width="medium"),
        "actie": st.column_config.TextColumn("Actie", width="large"),
        "datum_actie": st.column_config.DateColumn("Datum", format="DD/MM/YYYY"),
        "prioriteit": st.column_config.SelectboxColumn("Prioriteit", options=ACTION_PRIORITIES, width="small"),
        "status": st.column_config.SelectboxColumn("Status", options=ACTION_STATUSES, width="small"),
        "kanaal": st.column_config.SelectboxColumn("Kanaal", options=ACTION_CHANNELS, width="small"),
        "notities": st.column_config.TextColumn("Notities", width="large"),
        "aangemaakt_op": st.column_config.DateColumn("Aangemaakt", format="DD/MM/YYYY"),
        "afgerond_op": st.column_config.DateColumn("Afgerond", format="DD/MM/YYYY"),
        "cadans": st.column_config.TextColumn("Cadans", disabled=True, width="medium"),
        "cadans_stap": st.column_config.TextColumn("Stap", disabled=True, width="small"),
    }


# ---------------------------------------------------------------- sidebar
st.sidebar.markdown(
    """
    <div class="brand-card">
      <div class="brand-logo">🌞 Solvigo</div>
      <div class="brand-sub">CRM voor partners, projecten en opvolging</div>
    </div>
    """,
    unsafe_allow_html=True,
)
prijs = st.sidebar.number_input("Richtprijs per paneel (€)", min_value=0.0, value=st.session_state.get("prijs", 1.50), step=0.10)
st.session_state["prijs"] = prijs
if st.sidebar.button("🔄 Data vernieuwen", use_container_width=True):
    sheets.clear_all_caches()
    st.rerun()
st.sidebar.markdown(
    """
    <div class="side-note">
      <strong>Nieuwe structuur</strong><br>
      Installateurs staan bij <strong>Partners</strong>. Een concrete klant/opdracht staat bij <strong>Projecten</strong>. Iedere belactie of opvolging komt in het <strong>Actieblad</strong>.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- load
try:
    partners = sheets.load_partners()
    projects = sheets.load_projects()
    actions = sheets.load_actions()
    visits = sheets.load_visits()
    log = sheets.load_log()
    legacy = sheets.load_legacy_leads()
except KeyError:
    st.markdown(
        """
        <div class="hero">
            <div>
                <p class="eyebrow">Configuratie nodig</p>
                <h1>Solvigo CRM</h1>
                <p>De app is gedeployed. Alleen de Streamlit Secrets ontbreken nog.</p>
            </div>
            <div class="hero-panel"><div class="small">Status</div><div class="big">Secrets</div></div>
        </div>
        <div class="alert-card"><strong>Secrets ontbreken.</strong><br>Zet <code>[sheet].id</code> en <code>[gcp_service_account]</code> in je Streamlit Secrets.</div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()
except Exception as e:
    st.markdown(
        f"""
        <div class="alert-card"><strong>Google Sheet kan niet geladen worden.</strong><br>
        Foutmelding: {esc(e)}<br><br>
        Controleer of de Sheet gedeeld is met het service-account als <strong>Bewerker</strong>.</div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# derived
today = date.today()
if len(actions):
    actions["_bucket"] = actions.apply(lambda r: action_bucket(r, today), axis=1)
else:
    actions["_bucket"] = pd.Series(dtype=str)

open_actions = actions[actions["status"] == "Open"] if len(actions) else actions
late_actions = actions[actions["_bucket"] == "Te laat"].sort_values("datum_actie") if len(actions) else actions
today_actions = actions[actions["_bucket"] == "Vandaag"].sort_values("datum_actie") if len(actions) else actions
week_actions = actions[actions["_bucket"] == "Deze week"].sort_values("datum_actie") if len(actions) else actions
active_projects = projects[~projects["status"].isin(PROJECT_AFGEHANDELD)] if len(projects) else projects
pipeline_value = sum(project_value(r, prijs) for _, r in active_projects.iterrows()) if len(active_projects) else 0

st.markdown(
    f"""
    <div class="hero">
      <div>
        <p class="eyebrow">Solvigo CRM</p>
        <h1>Partners, projecten en actieblad</h1>
        <p>Installateurs worden nu als partners beheerd. Concrete opdrachten worden aparte projecten, met opvolgacties en plaatsbezoekverslagen.</p>
      </div>
      <div class="hero-panel">
        <div class="small">Te doen</div>
        <div class="big">{whole(len(late_actions) + len(today_actions))}</div>
        <div style="color:rgba(255,255,255,.72); font-size:.9rem;">te laat of vandaag</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs(["📊 Dashboard", "✅ Actieblad", "🗓 Agenda", "🏗 Projecten", "🤝 Partners", "📍 Plaatsbezoek", "🗂 Data & export"])

# ================================================================ DASHBOARD
with tabs[0]:
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Open acties", whole(len(open_actions)))
    k2.metric("Te laat", whole(len(late_actions)))
    k3.metric("Deze week", whole(len(week_actions)))
    k4.metric("Actieve projecten", whole(len(active_projects)))
    k5.metric("Pijplijnwaarde", euro(pipeline_value))

    c1, c2 = st.columns([1.1, 1])
    with c1:
        section("Prioriteit vandaag", "Werk eerst te late acties en acties van vandaag af.")
        urgent = pd.concat([late_actions, today_actions]).drop_duplicates(subset=["id"]).head(7) if len(actions) else actions
        if len(urgent):
            for _, r in urgent.iterrows():
                action_card(r)
        else:
            st.markdown('<div class="success-card"><strong>Geen dringende acties.</strong><br>Je opvolging is op dit moment onder controle.</div>', unsafe_allow_html=True)
    with c2:
        section("Projectfase")
        counts = projects["status"].value_counts().reindex(PROJECT_STATUSES).fillna(0).astype(int) if len(projects) else pd.Series(0, index=PROJECT_STATUSES)
        items = "".join(
            f'<div class="grid-item"><div class="label">{esc(status)}</div><div class="value">{int(count)}</div></div>'
            for status, count in counts.items()
        )
        st.markdown(f'<div class="grid">{items}</div>', unsafe_allow_html=True)

    section("Partnerwaarde", "Aantal projecten en gewonnen waarde per partner.")
    if len(partners) and len(projects):
        p = projects.copy()
        p["waarde"] = p.apply(lambda r: project_value(r, prijs), axis=1)
        partner_stats = p.groupby("partner_bedrijf", dropna=False).agg(projecten=("id", "count"), waarde=("waarde", "sum")).reset_index()
        partner_stats = partner_stats[partner_stats["partner_bedrijf"].astype(str).str.len() > 0].sort_values("waarde", ascending=False)
        if len(partner_stats):
            st.dataframe(partner_stats.rename(columns={"partner_bedrijf": "Partner", "projecten": "Projecten", "waarde": "Geschatte waarde"}), hide_index=True, use_container_width=True)
        else:
            st.info("Nog geen projecten die aan een partner gekoppeld zijn.")
    else:
        st.info("Voeg partners en projecten toe om partnerwaarde te zien.")

# ================================================================ ACTIEBLAD
with tabs[1]:
    section("Actieblad", "Dit is je dagelijkse werklijst: wie moet je bellen, mailen of opnieuw contacteren?")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Te laat", whole(len(late_actions)))
    a2.metric("Vandaag", whole(len(today_actions)))
    a3.metric("Deze week", whole(len(week_actions)))
    a4.metric("Open totaal", whole(len(open_actions)))

    with st.expander("➕ Nieuwe actie", expanded=len(open_actions) == 0):
        rels = relation_options(partners, projects)
        with st.form("new_action", clear_on_submit=True):
            if rels:
                labels = [r[3] for r in rels]
                rel_label = st.selectbox("Voor wie?", labels)
                rel_type, rel_id, rel_name, _ = rels[labels.index(rel_label)]
            else:
                rel_type, rel_id, rel_name = "Project", "", ""
                st.info("Maak eerst een partner of project aan. Je kan ook een losse actie zonder koppeling maken.")
                rel_name = st.text_input("Naam relatie")
            c1, c2, c3 = st.columns([2, 1, 1])
            actie = c1.text_input("Actie", placeholder="Bv. bellen voor afspraak / offerte opvolgen")
            datum_actie = c2.date_input("Datum", value=today + timedelta(days=2))
            prioriteit = c3.selectbox("Prioriteit", ACTION_PRIORITIES, index=1)
            c4, c5 = st.columns([1, 3])
            kanaal = c4.selectbox("Kanaal", ACTION_CHANNELS)
            notities = c5.text_input("Notities")
            ok = st.form_submit_button("Actie toevoegen", type="primary")
        if ok:
            if not actie.strip():
                st.warning("Vul een actie in.")
            else:
                sheets.append_action(dict(
                    id=new_id("A"), relatie_type=rel_type, relatie_id=rel_id, relatie_naam=rel_name,
                    actie=actie, datum_actie=datum_actie, prioriteit=prioriteit, status="Open",
                    kanaal=kanaal, notities=notities, aangemaakt_op=today, afgerond_op="",
                ))
                st.success("Actie toegevoegd.")
                st.rerun()

    section("Te laat en vandaag")
    urgent = pd.concat([late_actions, today_actions]).drop_duplicates(subset=["id"]) if len(actions) else actions
    if len(urgent):
        for _, r in urgent.iterrows():
            action_card(r)
    else:
        st.markdown('<div class="success-card"><strong>Geen acties te laat of vandaag.</strong></div>', unsafe_allow_html=True)

    section("Alle acties bewerken")
    f1, f2, f3 = st.columns([1, 1, 2])
    f_status = f1.multiselect("Status", ACTION_STATUSES, default=["Open"])
    f_prio = f2.multiselect("Prioriteit", ACTION_PRIORITIES)
    zoek = f3.text_input("Zoek actie/relatie", key="zoek_acties")
    action_view = actions.drop(columns=["_bucket"]).copy() if "_bucket" in actions.columns else actions.copy()
    if f_status:
        action_view = action_view[action_view["status"].isin(f_status)]
    if f_prio:
        action_view = action_view[action_view["prioriteit"].isin(f_prio)]
    if zoek:
        action_view = action_view[
            action_view["actie"].str.contains(zoek, case=False, na=False)
            | action_view["relatie_naam"].str.contains(zoek, case=False, na=False)
        ]
    edited_actions = st.data_editor(action_view, column_config=action_col_config(), num_rows="dynamic", use_container_width=True, hide_index=True, key="action_editor")
    csave, crefresh, _ = st.columns([1, 1, 4])
    if csave.button("💾 Acties opslaan", type="primary", use_container_width=True):
        edited_actions = edited_actions.copy()
        edited_actions["afgerond_op"] = edited_actions.apply(
            lambda r: today if r.get("status") == "Gedaan" and not isinstance(r.get("afgerond_op"), date) else r.get("afgerond_op"), axis=1
        )
        save_filtered_table(actions, edited_actions, "id", sheets.save_actions, drop_cols=["_bucket"])
        st.success("Acties opgeslagen.")
        st.rerun()
    if crefresh.button("🔄 Vernieuwen", use_container_width=True):
        sheets.clear_all_caches()
        st.rerun()

# ================================================================ AGENDA
with tabs[2]:
    section("Agenda", "Je opvolging op een tijdlijn. Vink af met ✓ — de volgende stap van een cadans plant zichzelf in.")

    # --- start een opvolgreeks (cadans) ---
    with st.expander("🔁 Opvolgreeks (cadans) starten", expanded=len(open_actions) == 0):
        st.caption("Kies een partner of project, kies een reeks, en de app plant stap 1 in. "
                   "Telkens je een stap afvinkt, verschijnt automatisch de volgende.")
        rels = relation_options(partners, projects)
        if not rels:
            st.info("Maak eerst een partner of project aan.")
        else:
            with st.form("start_cadans", clear_on_submit=True):
                labels = [r[3] for r in rels]
                c1, c2, c3 = st.columns([2, 2, 1])
                rel_label = c1.selectbox("Voor wie?", labels)
                cadans = c2.selectbox("Opvolgreeks", cadans_namen())
                startdatum = c3.date_input("Startdatum", value=today)
                stappen = cadans_stappen(cadans)
                st.markdown(
                    "<div class='caption2'>Reeks: " +
                    " → ".join(f"{s['label']} (+{s['wacht']}d)" for s in stappen) +
                    "</div>", unsafe_allow_html=True)
                start = st.form_submit_button("Reeks starten", type="primary")
            if start:
                rel_type, rel_id, rel_name, _ = rels[labels.index(rel_label)]
                eerste = cadans_actie_dict(rel_type, rel_id, rel_name, cadans, 0, startdatum, today)
                sheets.append_action(eerste)
                st.success(f"Reeks '{cadans}' gestart voor {rel_name}. Eerste stap: "
                           f"{eerste['actie']} op {date_label(eerste['datum_actie'])}.")
                st.rerun()

    # --- 14-daagse strip ---
    section("Komende 14 dagen")
    if len(open_actions):
        per_dag = {}
        for _, r in open_actions.iterrows():
            d = r.get("datum_actie")
            if isinstance(d, date):
                per_dag[d] = per_dag.get(d, 0) + 1
    else:
        per_dag = {}
    weekdagen = ["ma", "di", "wo", "do", "vr", "za", "zo"]
    cells = ""
    for n in range(14):
        d = today + timedelta(days=n)
        cnt = per_dag.get(d, 0)
        late = sum(v for k, v in per_dag.items() if k < today) if n == 0 else 0
        bg = "#0f766e" if cnt else "#ffffff"
        fg = "#ffffff" if cnt else "#94a3b8"
        ring = "border:2px solid #b42318;" if (n == 0 and late) else "border:1px solid var(--line);"
        badge = f'<div style="font-size:1.35rem;font-weight:850;color:{fg};">{cnt or "·"}</div>'
        latebadge = f'<div style="font-size:.7rem;color:#b42318;font-weight:850;">{late} te laat</div>' if (n == 0 and late) else '<div style="font-size:.7rem;">&nbsp;</div>'
        cells += (
            f'<div style="min-width:74px;background:{bg};{ring}border-radius:14px;'
            f'padding:.5rem;text-align:center;box-shadow:0 6px 16px rgba(15,34,31,.05);">'
            f'<div style="font-size:.72rem;color:{fg};text-transform:uppercase;font-weight:800;">{weekdagen[d.weekday()]}</div>'
            f'<div style="font-size:.8rem;color:{fg};font-weight:700;">{d.strftime("%d/%m")}</div>'
            f'{badge}{latebadge}</div>')
    st.markdown(f'<div style="display:flex;gap:.5rem;overflow-x:auto;padding:.3rem 0 .8rem 0;">{cells}</div>',
                unsafe_allow_html=True)

    # --- buckets met afrondknoppen ---
    buckets = [
        ("⚠ Te laat", late_actions),
        ("Vandaag", today_actions),
        ("Deze week", week_actions),
    ]
    for titel, data in buckets:
        section(f"{titel} ({len(data)})")
        if len(data):
            for _, r in data.iterrows():
                agenda_actie_kaart(r, actions, today)
        else:
            st.markdown('<div class="success-card"><strong>Niets hier.</strong></div>', unsafe_allow_html=True)

    later = actions[actions["_bucket"] == "Later"].sort_values("datum_actie") if len(actions) else actions
    if len(later):
        with st.expander(f"Later gepland ({len(later)})"):
            for _, r in later.iterrows():
                agenda_actie_kaart(r, actions, today)


# ================================================================ PROJECTEN
with tabs[3]:
    section("Projecten", "Concrete opdrachten of eindklanten. Een project kan gekoppeld zijn aan een partner/installateur.")

    with st.expander("➕ Nieuw project", expanded=len(projects) == 0):
        p_opts = partner_select_options(partners)
        with st.form("new_project", clear_on_submit=True):
            c1, c2 = st.columns(2)
            projectnaam = c1.text_input("Projectnaam *", placeholder="Bv. Janssens Agro — reiniging 850 panelen")
            klant = c2.text_input("Klantbedrijf")
            contact = c1.text_input("Contactpersoon")
            email = c2.text_input("E-mail")
            tel = c1.text_input("Telefoon")
            adres = c2.text_input("Adres")
            regio = c1.text_input("Regio")
            panelen = c2.number_input("Aantal panelen", min_value=0, step=50)
            bron_type = c1.selectbox("Bron type", BRON_TYPES)
            partner_label = c2.selectbox("Doorverwezen door / partner", [name for _, name in p_opts])
            partner_id = p_opts[[name for _, name in p_opts].index(partner_label)][0]
            status = c1.selectbox("Status", PROJECT_STATUSES, index=PROJECT_STATUSES.index("Te contacteren"))
            waarde = c2.number_input("Verwachte waarde (€) optioneel", min_value=0.0, step=100.0, value=0.0)
            actie = c1.text_input("Volgende actie", value="Eindklant contacteren")
            datum_actie = c2.date_input("Datum actie", value=today + timedelta(days=2))
            notities = st.text_area("Notities")
            ok = st.form_submit_button("Project toevoegen", type="primary")
        if ok:
            if not projectnaam.strip():
                st.warning("Vul minstens een projectnaam in.")
            else:
                partner_bedrijf = "" if partner_label == "Geen partner/installateur" else partner_label
                pid = new_id("P")
                sheets.append_project(dict(
                    id=pid, projectnaam=projectnaam, klant_bedrijf=klant, contactpersoon=contact, email=email,
                    telefoon=tel, adres=adres, regio=regio, aantal_panelen=panelen, partner_id=partner_id,
                    partner_bedrijf=partner_bedrijf, bron_type=bron_type, status=status, eerste_contact="",
                    laatste_contact="", volgende_actie=actie, datum_actie=datum_actie, verwachte_waarde=waarde,
                    notities=notities,
                ))
                sheets.append_action(dict(
                    id=new_id("A"), relatie_type="Project", relatie_id=pid, relatie_naam=projectnaam,
                    actie=actie, datum_actie=datum_actie, prioriteit="Normaal", status="Open", kanaal="Telefoon",
                    notities="Automatisch aangemaakt bij nieuw project", aangemaakt_op=today, afgerond_op="",
                ))
                st.success("Project en eerste actie toegevoegd.")
                st.rerun()

    f1, f2, f3 = st.columns([1.4, 1.6, 2.2])
    f_status = f1.multiselect("Status project", PROJECT_STATUSES)
    f_bron = f2.multiselect("Bron type", BRON_TYPES)
    zoek = f3.text_input("Zoek project/klant", key="zoek_projecten")
    view = projects.copy()
    if f_status:
        view = view[view["status"].isin(f_status)]
    if f_bron:
        view = view[view["bron_type"].isin(f_bron)]
    if zoek:
        view = view[view["projectnaam"].str.contains(zoek, case=False, na=False) | view["klant_bedrijf"].str.contains(zoek, case=False, na=False)]
    edited_projects = st.data_editor(view, column_config=project_col_config(partners), num_rows="dynamic", use_container_width=True, hide_index=True, key="project_editor")
    s1, s2, _ = st.columns([1, 1, 4])
    if s1.button("💾 Projecten opslaan", type="primary", use_container_width=True):
        edited_projects = edited_projects.copy()
        # Herkoppel partner_id op basis van partner_bedrijf waar mogelijk
        partner_name_to_id = {name: pid for pid, name in partner_select_options(partners)}
        edited_projects["partner_id"] = edited_projects["partner_bedrijf"].map(partner_name_to_id).fillna(edited_projects["partner_id"])
        save_filtered_table(projects, edited_projects, "id", sheets.save_projects)
        st.success("Projecten opgeslagen.")
        st.rerun()
    if s2.button("🔄 Vernieuwen", use_container_width=True, key="refresh_projects"):
        sheets.clear_all_caches()
        st.rerun()

    st.divider()
    section("Projectfiche")
    if len(projects):
        ids = projects["id"].tolist()
        selected = st.selectbox("Kies project", ids, format_func=lambda i: projects.loc[projects["id"] == i, "projectnaam"].iloc[0] or "Naamloos project")
        row = projects[projects["id"] == selected].iloc[0].to_dict()
        left, right = st.columns([3, 1.35])
        with left:
            st.markdown(f"### {esc(row.get('projectnaam'))}", unsafe_allow_html=True)
            with st.form("edit_project"):
                c1, c2 = st.columns(2)
                projectnaam = c1.text_input("Projectnaam", row["projectnaam"])
                klant = c2.text_input("Klantbedrijf", row["klant_bedrijf"])
                contact = c1.text_input("Contactpersoon", row["contactpersoon"])
                email = c2.text_input("E-mail", row["email"])
                tel = c1.text_input("Telefoon", row["telefoon"])
                adres = c2.text_input("Adres", row["adres"])
                regio = c1.text_input("Regio", row["regio"])
                panelen = c2.number_input("Aantal panelen", min_value=0, step=50, value=int(row["aantal_panelen"] or 0), key="edit_proj_panelen")
                bron_type = c1.selectbox("Bron type", BRON_TYPES, index=BRON_TYPES.index(row["bron_type"]) if row["bron_type"] in BRON_TYPES else 0)
                p_opts = partner_select_options(partners)
                names = [name for _, name in p_opts]
                current_partner = row.get("partner_bedrijf") or "Geen partner/installateur"
                partner_label = c2.selectbox("Partner", names, index=names.index(current_partner) if current_partner in names else 0, key="edit_project_partner")
                partner_id = p_opts[names.index(partner_label)][0]
                status = c1.selectbox("Status", PROJECT_STATUSES, index=PROJECT_STATUSES.index(row["status"]) if row["status"] in PROJECT_STATUSES else 0)
                waarde = c2.number_input("Verwachte waarde (€)", min_value=0.0, step=100.0, value=float(row["verwachte_waarde"] or 0), key="edit_project_value")
                actie = c1.text_input("Volgende actie", row["volgende_actie"])
                dval = row["datum_actie"] if isinstance(row["datum_actie"], date) else today + timedelta(days=7)
                datum_actie = c2.date_input("Datum actie", value=dval, key="edit_project_date")
                notities = st.text_area("Notities", row["notities"])
                ok = st.form_submit_button("Project opslaan", type="primary")
            if ok:
                full = projects.copy()
                idx = full.index[full["id"] == selected][0]
                full.loc[idx, PROJECT_HEADERS] = [
                    selected, projectnaam, klant, contact, email, tel, adres, regio, panelen, partner_id,
                    "" if partner_label == "Geen partner/installateur" else partner_label, bron_type, status,
                    row["eerste_contact"], row["laatste_contact"], actie, datum_actie, waarde, notities,
                ]
                sheets.save_projects(full)
                st.success("Project opgeslagen.")
                st.rerun()
        with right:
            waarde_calc = project_value(row, prijs)
            st.metric("Geschatte waarde", euro(waarde_calc))
            st.caption(f"{whole(row.get('aantal_panelen'))} panelen × € {prijs:.2f}, of ingevulde waarde")
            st.markdown(status_pill(row.get("status")), unsafe_allow_html=True)
            st.markdown("#### Offertebrug")
            st.text_area("Kopieer naar offerte-tool", offerte_tekst_project(row, prijs), height=245)

        st.markdown("### Contactmoment + volgende actie")
        with st.form("project_log", clear_on_submit=True):
            c1, c2 = st.columns([1, 3])
            soort = c1.selectbox("Soort", LOG_SOORTEN, key="project_log_soort")
            notitie = c2.text_input("Notitie", key="project_log_notitie")
            n1, n2, n3 = st.columns([2, 1, 1])
            next_action = n1.text_input("Nieuwe volgende actie", placeholder="Bv. plaatsbezoek inplannen / offerte opvolgen")
            next_date = n2.date_input("Datum", value=today + timedelta(days=7), key="project_next_date")
            prio = n3.selectbox("Prioriteit", ACTION_PRIORITIES, index=1, key="project_next_prio")
            oklog = st.form_submit_button("Loggen en eventueel actie maken", type="primary")
        if oklog:
            sheets.append_log(dict(id=new_id("L"), relatie_type="Project", relatie_id=selected, relatie_naam=row["projectnaam"], datum=today, soort=soort, notitie=notitie))
            full = projects.copy()
            idx = full.index[full["id"] == selected][0]
            full.loc[idx, "laatste_contact"] = today
            if not isinstance(row["eerste_contact"], date):
                full.loc[idx, "eerste_contact"] = today
            if next_action.strip():
                full.loc[idx, "volgende_actie"] = next_action
                full.loc[idx, "datum_actie"] = next_date
                sheets.append_action(dict(id=new_id("A"), relatie_type="Project", relatie_id=selected, relatie_naam=row["projectnaam"], actie=next_action, datum_actie=next_date, prioriteit=prio, status="Open", kanaal="Telefoon", notities="Aangemaakt vanuit projectfiche", aangemaakt_op=today, afgerond_op=""))
            sheets.save_projects(full)
            st.success("Geloggd.")
            st.rerun()
    else:
        st.info("Nog geen projecten.")

# ================================================================ PARTNERS
with tabs[4]:
    section("Partners / installateurs", "Hier beheer je installateurs en O&M-partijen als relaties. Hun doorverwijzingen worden aparte projecten.")

    with st.expander("➕ Nieuwe partner", expanded=len(partners) == 0):
        with st.form("new_partner", clear_on_submit=True):
            c1, c2 = st.columns(2)
            bedrijf = c1.text_input("Bedrijf *")
            typ = c2.selectbox("Type", PARTNER_TYPES)
            contact = c1.text_input("Contactpersoon")
            functie = c2.text_input("Functie")
            email = c1.text_input("E-mail")
            tel = c2.text_input("Telefoon")
            regio = c1.text_input("Regio")
            website = c2.text_input("Website")
            bron = c1.text_input("Bron")
            status = c2.selectbox("Status", PARTNER_STATUSES, index=PARTNER_STATUSES.index("Te contacteren"))
            actie = c1.text_input("Volgende actie", value="Samenwerking voorstellen")
            datum_actie = c2.date_input("Datum actie", value=today + timedelta(days=3), key="new_partner_date")
            notities = st.text_area("Notities")
            ok = st.form_submit_button("Partner toevoegen", type="primary")
        if ok:
            if not bedrijf.strip():
                st.warning("Vul minstens een bedrijfsnaam in.")
            else:
                pid = new_id("R")
                sheets.append_partner(dict(id=pid, bedrijf=bedrijf, type=typ, contactpersoon=contact, functie=functie, email=email, telefoon=tel, regio=regio, website=website, status=status, bron=bron, eerste_contact="", laatste_contact="", volgende_actie=actie, datum_actie=datum_actie, notities=notities))
                sheets.append_action(dict(id=new_id("A"), relatie_type="Partner", relatie_id=pid, relatie_naam=bedrijf, actie=actie, datum_actie=datum_actie, prioriteit="Normaal", status="Open", kanaal="Telefoon", notities="Automatisch aangemaakt bij nieuwe partner", aangemaakt_op=today, afgerond_op=""))
                st.success("Partner en eerste actie toegevoegd.")
                st.rerun()

    f1, f2, f3 = st.columns([1.4, 1.4, 2.2])
    f_status = f1.multiselect("Partnerstatus", PARTNER_STATUSES)
    f_type = f2.multiselect("Partner type", PARTNER_TYPES)
    zoek = f3.text_input("Zoek partner", key="zoek_partners")
    view = partners.copy()
    if f_status:
        view = view[view["status"].isin(f_status)]
    if f_type:
        view = view[view["type"].isin(f_type)]
    if zoek:
        view = view[view["bedrijf"].str.contains(zoek, case=False, na=False) | view["contactpersoon"].str.contains(zoek, case=False, na=False)]
    edited_partners = st.data_editor(view, column_config=partner_col_config(), num_rows="dynamic", use_container_width=True, hide_index=True, key="partner_editor")
    ps1, ps2, _ = st.columns([1, 1, 4])
    if ps1.button("💾 Partners opslaan", type="primary", use_container_width=True):
        save_filtered_table(partners, edited_partners, "id", sheets.save_partners)
        st.success("Partners opgeslagen.")
        st.rerun()
    if ps2.button("🔄 Vernieuwen", use_container_width=True, key="refresh_partners"):
        sheets.clear_all_caches()
        st.rerun()

    st.divider()
    section("Partnerfiche + doorverwijzing")
    if len(partners):
        ids = partners["id"].tolist()
        selected = st.selectbox("Kies partner", ids, format_func=lambda i: partners.loc[partners["id"] == i, "bedrijf"].iloc[0] or "Naamloze partner")
        row = partners[partners["id"] == selected].iloc[0].to_dict()
        linked_projects = projects[projects["partner_id"] == selected] if len(projects) else projects
        col_left, col_right = st.columns([2.3, 1.2])
        with col_left:
            st.markdown(f"### {esc(row.get('bedrijf'))}", unsafe_allow_html=True)
            st.markdown(status_pill(row.get("status")), unsafe_allow_html=True)
            st.write(f"**Contact:** {row.get('contactpersoon') or '—'} · {row.get('email') or '—'} · {row.get('telefoon') or '—'}")
            st.write(f"**Regio:** {row.get('regio') or '—'}")
            if row.get("notities"):
                st.info(row.get("notities"))
        with col_right:
            waarde_partner = sum(project_value(r, prijs) for _, r in linked_projects.iterrows()) if len(linked_projects) else 0
            st.metric("Doorverwezen projecten", whole(len(linked_projects)))
            st.metric("Geschatte waarde", euro(waarde_partner))

        with st.expander("➡ Project aanmaken uit doorverwijzing", expanded=False):
            st.caption("Gebruik dit wanneer een installateur zegt: ‘Neem contact op met die klant.’ De installateur blijft partner, de klant wordt een apart project.")
            with st.form("ref_project", clear_on_submit=True):
                c1, c2 = st.columns(2)
                projectnaam = c1.text_input("Projectnaam *", placeholder="Bv. Klantnaam — reiniging zonnepanelen")
                klant = c2.text_input("Klantbedrijf / persoon")
                contact = c1.text_input("Contactpersoon klant")
                email = c2.text_input("E-mail klant")
                tel = c1.text_input("Telefoon klant")
                adres = c2.text_input("Adres")
                regio = c1.text_input("Regio", value=row.get("regio", ""))
                panelen = c2.number_input("Aantal panelen", min_value=0, step=50, key="ref_panelen")
                actie = c1.text_input("Eerste actie", value="Eindklant contacteren")
                datum_actie = c2.date_input("Datum actie", value=today + timedelta(days=1), key="ref_date")
                notities = st.text_area("Notities", value=f"Doorverwezen door {row.get('bedrijf', '')}.")
                ok = st.form_submit_button("Doorverwezen project toevoegen", type="primary")
            if ok:
                if not projectnaam.strip():
                    st.warning("Vul minstens een projectnaam in.")
                else:
                    pid = new_id("P")
                    bron_type = "Doorverwijzing installateur" if row.get("type") == "Installateur" else "Doorverwijzing O&M"
                    sheets.append_project(dict(id=pid, projectnaam=projectnaam, klant_bedrijf=klant, contactpersoon=contact, email=email, telefoon=tel, adres=adres, regio=regio, aantal_panelen=panelen, partner_id=selected, partner_bedrijf=row["bedrijf"], bron_type=bron_type, status="Te contacteren", eerste_contact="", laatste_contact="", volgende_actie=actie, datum_actie=datum_actie, verwachte_waarde=0, notities=notities))
                    sheets.append_action(dict(id=new_id("A"), relatie_type="Project", relatie_id=pid, relatie_naam=projectnaam, actie=actie, datum_actie=datum_actie, prioriteit="Hoog", status="Open", kanaal="Telefoon", notities=f"Doorverwijzing via {row.get('bedrijf', '')}", aangemaakt_op=today, afgerond_op=""))
                    sheets.append_log(dict(id=new_id("L"), relatie_type="Partner", relatie_id=selected, relatie_naam=row["bedrijf"], datum=today, soort="Doorverwijzing", notitie=f"Project doorverwezen: {projectnaam}"))
                    st.success("Doorverwezen project, actie en partnerlog toegevoegd.")
                    st.rerun()

        st.markdown("#### Projecten via deze partner")
        if len(linked_projects):
            st.dataframe(linked_projects[["projectnaam", "klant_bedrijf", "status", "aantal_panelen", "volgende_actie", "datum_actie"]].rename(columns=LABELS), hide_index=True, use_container_width=True)
        else:
            st.info("Nog geen projecten gekoppeld aan deze partner.")

        st.markdown("#### Contactmoment partner loggen")
        with st.form("partner_log", clear_on_submit=True):
            c1, c2 = st.columns([1, 3])
            soort = c1.selectbox("Soort", LOG_SOORTEN, key="partner_log_soort")
            notitie = c2.text_input("Notitie", key="partner_log_notitie")
            n1, n2, n3 = st.columns([2, 1, 1])
            next_action = n1.text_input("Nieuwe volgende actie", placeholder="Bv. voorstel mailen / volgende week bellen")
            next_date = n2.date_input("Datum", value=today + timedelta(days=7), key="partner_next_date")
            prio = n3.selectbox("Prioriteit", ACTION_PRIORITIES, index=1, key="partner_next_prio")
            oklog = st.form_submit_button("Loggen en eventueel actie maken", type="primary")
        if oklog:
            sheets.append_log(dict(id=new_id("L"), relatie_type="Partner", relatie_id=selected, relatie_naam=row["bedrijf"], datum=today, soort=soort, notitie=notitie))
            full = partners.copy()
            idx = full.index[full["id"] == selected][0]
            full.loc[idx, "laatste_contact"] = today
            if not isinstance(row["eerste_contact"], date):
                full.loc[idx, "eerste_contact"] = today
            if next_action.strip():
                full.loc[idx, "volgende_actie"] = next_action
                full.loc[idx, "datum_actie"] = next_date
                sheets.append_action(dict(id=new_id("A"), relatie_type="Partner", relatie_id=selected, relatie_naam=row["bedrijf"], actie=next_action, datum_actie=next_date, prioriteit=prio, status="Open", kanaal="Telefoon", notities="Aangemaakt vanuit partnerfiche", aangemaakt_op=today, afgerond_op=""))
            sheets.save_partners(full)
            st.success("Geloggd.")
            st.rerun()
    else:
        st.info("Nog geen partners.")

# ================================================================ PLAATSBEZOEK
with tabs[5]:
    section("Plaatsbezoek", "Maak een verslag per project. Foto's bewaar je praktisch als Google Drive-links in het verslag.")
    st.markdown(
        '<div class="soft-card"><strong>Foto-aanpak</strong><br>Google Sheets is geen goede fotomap. Upload foto\'s best naar een Google Drive-map en plak de deel-links hieronder. De app bewaart die links bij het plaatsbezoek.</div>',
        unsafe_allow_html=True,
    )

    if len(projects):
        with st.expander("➕ Nieuw plaatsbezoekverslag", expanded=len(visits) == 0):
            project_ids = projects["id"].tolist()
            with st.form("new_visit", clear_on_submit=True):
                project_id = st.selectbox("Project", project_ids, format_func=lambda i: projects.loc[projects["id"] == i, "projectnaam"].iloc[0] or "Naamloos project")
                prow = projects[projects["id"] == project_id].iloc[0].to_dict()
                c1, c2 = st.columns(2)
                datum = c1.date_input("Datum plaatsbezoek", value=today)
                contact_tp = c2.text_input("Contact ter plaatse", value=prow.get("contactpersoon", ""))
                adres = c1.text_input("Adres", value=prow.get("adres", ""))
                panelen_gezien = c2.number_input("Panelen gezien", min_value=0, step=50, value=int(prow.get("aantal_panelen") or 0))
                dak_type = c1.selectbox("Daktype", VISIT_DAK_TYPES)
                helling = c2.text_input("Helling / opstelling", placeholder="Bv. 15°, plat dak met ballast")
                vervuiling = c1.selectbox("Vervuiling", VISIT_VERVUILING, index=1)
                toegang = c2.selectbox("Toegang", VISIT_TOEGANG)
                waterpunt = c1.text_input("Waterpunt", placeholder="Bv. regenput / buitenkraan / geen")
                veiligheid = c2.text_input("Veiligheid", placeholder="Bv. dakrand, lichtkoepels, valbeveiliging nodig")
                verslag = st.text_area("Verslag", height=170, placeholder="Situatie, risico's, aanpak, materiaal, bijzonderheden...")
                foto_links = st.text_area("Foto-links", placeholder="Plak hier Google Drive-links, één per regel")
                n1, n2 = st.columns(2)
                volgende_actie = n1.text_input("Volgende actie", value="Offerte maken")
                datum_actie = n2.date_input("Datum volgende actie", value=today + timedelta(days=1), key="visit_next_date")
                ok = st.form_submit_button("Verslag opslaan", type="primary")
            if ok:
                vid = new_id("V")
                sheets.append_visit(dict(id=vid, project_id=project_id, projectnaam=prow.get("projectnaam", ""), datum=datum, contact_ter_plaatse=contact_tp, adres=adres, aantal_panelen_gezien=panelen_gezien, dak_type=dak_type, helling=helling, vervuiling=vervuiling, toegang=toegang, waterpunt=waterpunt, veiligheid=veiligheid, verslag=verslag, foto_links=foto_links, volgende_actie=volgende_actie, datum_actie=datum_actie, aangemaakt_op=today))
                # project bijwerken + actie aanmaken
                full = projects.copy()
                idx = full.index[full["id"] == project_id][0]
                full.loc[idx, "status"] = "Offerte maken" if volgende_actie.lower().startswith("offerte") else "Verslag maken"
                full.loc[idx, "volgende_actie"] = volgende_actie
                full.loc[idx, "datum_actie"] = datum_actie
                sheets.save_projects(full)
                sheets.append_action(dict(id=new_id("A"), relatie_type="Project", relatie_id=project_id, relatie_naam=prow.get("projectnaam", ""), actie=volgende_actie, datum_actie=datum_actie, prioriteit="Hoog", status="Open", kanaal="Offerte", notities="Aangemaakt vanuit plaatsbezoekverslag", aangemaakt_op=today, afgerond_op=""))
                sheets.append_log(dict(id=new_id("L"), relatie_type="Project", relatie_id=project_id, relatie_naam=prow.get("projectnaam", ""), datum=today, soort="Bezoek", notitie=f"Plaatsbezoekverslag opgeslagen. Vervuiling: {vervuiling}. Toegang: {toegang}."))
                st.success("Plaatsbezoekverslag, vervolgactie en log opgeslagen.")
                st.rerun()
    else:
        st.info("Maak eerst een project aan voordat je een plaatsbezoekverslag kunt maken.")

    section("Verslagen")
    if len(visits):
        st.dataframe(visits[["datum", "projectnaam", "contact_ter_plaatse", "vervuiling", "toegang", "volgende_actie", "datum_actie"]].rename(columns=LABELS), hide_index=True, use_container_width=True)
        selected_visit = st.selectbox("Bekijk verslag", visits["id"].tolist(), format_func=lambda i: f"{visits.loc[visits['id'] == i, 'projectnaam'].iloc[0]} — {date_label(visits.loc[visits['id'] == i, 'datum'].iloc[0])}")
        v = visits[visits["id"] == selected_visit].iloc[0].to_dict()
        st.markdown(f"### {esc(v.get('projectnaam'))} — {date_label(v.get('datum'))}", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Panelen gezien", whole(v.get("aantal_panelen_gezien")))
        c2.metric("Vervuiling", v.get("vervuiling") or "—")
        c3.metric("Toegang", v.get("toegang") or "—")
        st.write(f"**Adres:** {v.get('adres') or '—'}")
        st.write(f"**Waterpunt:** {v.get('waterpunt') or '—'}")
        st.write(f"**Veiligheid:** {v.get('veiligheid') or '—'}")
        st.text_area("Verslagtekst", v.get("verslag", ""), height=180, disabled=True)
        if v.get("foto_links"):
            st.markdown("**Foto-links**")
            links = [x.strip() for x in str(v.get("foto_links", "")).splitlines() if x.strip()]
            for link in links:
                st.write(link)
    else:
        st.info("Nog geen plaatsbezoekverslagen.")

# ================================================================ DATA & EXPORT
with tabs[6]:
    section("Data & export", "Exporteer alles naar Excel en migreer oude leads indien nodig.")
    st.download_button(
        "⬇ Exporteer volledige CRM naar Excel",
        to_excel_bytes(partners, projects, actions.drop(columns=["_bucket"]) if "_bucket" in actions.columns else actions, visits, log),
        file_name="solvigo_crm_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    st.markdown("### Logboek")
    if len(log):
        st.dataframe(log.sort_values("datum", ascending=False).rename(columns=LABELS), hide_index=True, use_container_width=True)
    else:
        st.info("Nog geen logboekitems.")

    st.markdown("### Oude Leads-tab migreren")
    if len(legacy):
        st.info(f"Ik vond {len(legacy)} oude lead(s) in tabblad 'Leads'. Je kan ze splitsen naar Partners en Projecten. Het oude tabblad blijft bestaan als backup.")
        if st.button("Oude Leads splitsen naar Partners + Projecten", type="primary"):
            new_partners = []
            new_projects = []
            new_actions = []
            for _, r in legacy.iterrows():
                if r.get("type") in LEGACY_PARTNER_TYPES:
                    rid = new_id("R")
                    status = "Gecontacteerd" if r.get("status") in ["Gecontacteerd", "Opvolgen", "Interesse / gesprek"] else "Nieuw"
                    new_partners.append(dict(id=rid, bedrijf=r.get("bedrijf", ""), type=r.get("type", "Installateur"), contactpersoon=r.get("contactpersoon", ""), functie=r.get("functie", ""), email=r.get("email", ""), telefoon=r.get("telefoon", ""), regio=r.get("regio", ""), website="", status=status, bron=r.get("bron", ""), eerste_contact=r.get("eerste_contact", ""), laatste_contact=r.get("laatste_contact", ""), volgende_actie=r.get("volgende_actie", ""), datum_actie=r.get("datum_actie", ""), notities=r.get("notities", "")))
                    if r.get("volgende_actie"):
                        new_actions.append(dict(id=new_id("A"), relatie_type="Partner", relatie_id=rid, relatie_naam=r.get("bedrijf", ""), actie=r.get("volgende_actie", ""), datum_actie=r.get("datum_actie", ""), prioriteit="Normaal", status="Open", kanaal="Telefoon", notities="Gemigreerd uit oude Leads-tab", aangemaakt_op=today, afgerond_op=""))
                else:
                    pid = new_id("P")
                    new_projects.append(dict(id=pid, projectnaam=r.get("bedrijf", ""), klant_bedrijf=r.get("bedrijf", ""), contactpersoon=r.get("contactpersoon", ""), email=r.get("email", ""), telefoon=r.get("telefoon", ""), adres="", regio=r.get("regio", ""), aantal_panelen=r.get("aantal_panelen", 0), partner_id="", partner_bedrijf="", bron_type=r.get("bron", "Los project") if r.get("bron") in BRON_TYPES else "Andere", status="Te contacteren" if r.get("status") in ["Nieuw", "Gecontacteerd", "Opvolgen"] else r.get("status", "Te contacteren"), eerste_contact=r.get("eerste_contact", ""), laatste_contact=r.get("laatste_contact", ""), volgende_actie=r.get("volgende_actie", ""), datum_actie=r.get("datum_actie", ""), verwachte_waarde=0, notities=r.get("notities", "")))
                    if r.get("volgende_actie"):
                        new_actions.append(dict(id=new_id("A"), relatie_type="Project", relatie_id=pid, relatie_naam=r.get("bedrijf", ""), actie=r.get("volgende_actie", ""), datum_actie=r.get("datum_actie", ""), prioriteit="Normaal", status="Open", kanaal="Telefoon", notities="Gemigreerd uit oude Leads-tab", aangemaakt_op=today, afgerond_op=""))
            if new_partners:
                sheets.save_partners(pd.concat([partners, pd.DataFrame(new_partners).reindex(columns=PARTNER_HEADERS)], ignore_index=True))
            if new_projects:
                sheets.save_projects(pd.concat([projects, pd.DataFrame(new_projects).reindex(columns=PROJECT_HEADERS)], ignore_index=True))
            if new_actions:
                actions_clean = actions.drop(columns=["_bucket"]) if "_bucket" in actions.columns else actions
                sheets.save_actions(pd.concat([actions_clean, pd.DataFrame(new_actions).reindex(columns=ACTION_HEADERS)], ignore_index=True))
            st.success("Migratie uitgevoerd. Je oude Leads-tab is niet verwijderd.")
            st.rerun()
    else:
        st.caption("Geen oude Leads-tab met data gevonden.")

    with st.expander("Technische tabbladen in Google Sheets"):
        st.write("De app gebruikt nu deze tabbladen:")
        st.code("Partners\nProjecten\nActies\nPlaatsbezoeken\nLog")
