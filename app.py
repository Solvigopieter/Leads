"""Solvigo CRM — professionele structuur: partners, klanten, projecten, actieblad en plaatsbezoeken."""
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
    CUSTOMER_HEADERS,
    CUSTOMER_STATUSES,
    CUSTOMER_TYPES,
    KANBAN_STAGES,
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
    as_date,
    cadans_actie_dict,
    cadans_namen,
    cadans_stappen,
    cadans_volgende,
    euro,
    new_id,
    next_action_for_status,
    offerte_tekst_project,
    project_rotting,
    project_value,
    weighted_value,
    whole,
)

st.set_page_config(page_title="Solvigo CRM", page_icon="🌞", layout="wide")

CSS = """
<style>
:root { --ink:#10231f; --muted:#64748b; --line:#e1e8e4; --bg:#f6f8fa; --card:#fff; --green:#0f766e; --green-dark:#0b3b35; --gold:#f2b84b; --danger:#b42318; }
.stApp { background:#f6f8fa; }
[data-testid="stHeader"] { background:rgba(246,248,250,.85); backdrop-filter: blur(8px); }
[data-testid="stSidebar"] { background:#edf5f0; border-right:1px solid var(--line); }
.block-container { padding-top:1.3rem; max-width:1460px; }
h1,h2,h3 { color:var(--ink); letter-spacing:-.025em; }
.hero { background:linear-gradient(120deg,#0b3b35 0%,#0f766e 62%,#12857a 100%); color:white; border-radius:20px; padding:1.55rem 1.8rem; margin-bottom:1rem; display:flex; justify-content:space-between; gap:1.2rem; box-shadow:0 8px 24px rgba(11,59,53,.16); }
.hero h1 { color:white; font-size:2.1rem; margin:.1rem 0 .35rem 0; }
.hero p { color:rgba(255,255,255,.82); margin:0; max-width:900px; }
.eyebrow { color:#f8d78b!important; text-transform:uppercase; letter-spacing:.15em; font-size:.74rem!important; font-weight:850; margin-bottom:.25rem!important; }
.hero-panel { min-width:220px; background:rgba(255,255,255,.12); border:1px solid rgba(255,255,255,.22); border-radius:16px; padding:1rem; }
.hero-panel .small { color:rgba(255,255,255,.72); font-size:.78rem; text-transform:uppercase; letter-spacing:.08em; font-weight:800; }
.hero-panel .big { color:white; font-size:2rem; font-weight:850; margin-top:.1rem; }
.brand-card { background:linear-gradient(145deg,#fff,#e8f3ee); border:1px solid var(--line); border-radius:18px; padding:1rem; margin-bottom:1rem; box-shadow:0 2px 8px rgba(15,34,31,.05); }
.brand-logo { font-size:1.5rem; font-weight:850; color:var(--ink); letter-spacing:-.04em; }
.brand-sub { color:var(--muted); font-size:.86rem; }
.side-note { background:rgba(15,118,110,.08); border:1px solid rgba(15,118,110,.18); border-radius:14px; padding:.85rem; color:var(--ink); font-size:.88rem; margin-top:1rem; }
div[data-testid="stMetric"] { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:.85rem 1rem; box-shadow:0 2px 6px rgba(15,34,31,.055); }
div[data-testid="stMetricValue"] { color:var(--ink); font-weight:850; font-size:1.5rem; }
div[data-testid="stMetric"] label { color:var(--muted)!important; }
.section-title { margin:1.1rem 0 .65rem 0; }
.section-title h2,.section-title h3 { margin:0; }
.caption2 { color:var(--muted); font-size:.9rem; margin-top:-.15rem; margin-bottom:.75rem; }
.soft-card { background:#fff; border:1px solid var(--line); border-radius:16px; padding:1rem 1.1rem; box-shadow:0 2px 8px rgba(15,34,31,.055); margin-bottom:.75rem; }
.alert-card { background:#fff7ed; border:1px solid #fed7aa; color:#7c2d12; border-radius:18px; padding:1.1rem 1.25rem; margin:1rem 0; }
.success-card { background:#ecfdf5; border:1px solid #bbf7d0; color:#064e3b; border-radius:18px; padding:1.1rem 1.25rem; margin:1rem 0; }
.empty-state { background:#fff; border:1px dashed #c9d8d0; border-radius:20px; padding:1.6rem; text-align:center; color:var(--ink); }
.status-pill { display:inline-flex; align-items:center; border-radius:999px; padding:.24rem .58rem; font-size:.76rem; font-weight:850; color:#12352f; border:1px solid rgba(16,35,31,.08); white-space:nowrap; }
.nudge { display:flex; gap:.7rem; align-items:flex-start; background:#fff; border:1px solid #e6ebe9; border-left:4px solid #94a3b8; border-radius:12px; padding:.7rem .9rem; margin-bottom:.55rem; box-shadow:0 2px 6px rgba(15,34,31,.05); }
.nudge.warn { border-left-color:#b42318; } .nudge.info { border-left-color:#0f766e; } .nudge.gold { border-left-color:#f2b84b; }
.nudge .ic { font-size:1.1rem; line-height:1.3; } .nudge .tx { font-size:.92rem; color:#10231f; } .nudge .tx b { color:#0b3b35; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(185px,1fr)); gap:.8rem; margin:.4rem 0 1.2rem 0; }
.grid-item { background:#fff; border:1px solid var(--line); border-radius:16px; padding:.9rem; box-shadow:0 2px 8px rgba(15,34,31,.045); }
.grid-item .label { color:var(--muted); font-size:.76rem; font-weight:850; text-transform:uppercase; letter-spacing:.08em; }
.grid-item .value { color:var(--ink); font-size:1.55rem; font-weight:850; margin-top:.15rem; }
div[data-testid="stTabs"] button { border-radius:999px; padding:.35rem .85rem; }
div[data-testid="stTabs"] [aria-selected="true"] { background:#e7f5f1; color:#0f766e; font-weight:850; }
.pd-board { display:flex; gap:14px; overflow-x:auto; padding:4px 2px 14px; }
.pd-col { min-width:230px; max-width:255px; flex:0 0 auto; }
.pd-colhead { padding:2px 4px 9px; }
.pd-stage { font-weight:850; color:#0b3b35; font-size:.95rem; letter-spacing:-.01em; }
.pd-sub { color:#64748b; font-size:.78rem; font-weight:800; margin-top:2px; }
.pd-track { border-top:2px solid #e2e8e6; padding-top:9px; display:flex; flex-direction:column; gap:8px; min-height:60px; }
.pd-card { background:#fff; border:1px solid #e6ebe9; border-radius:10px; padding:10px 11px; box-shadow:0 1px 2px rgba(15,34,31,.06); }
.pd-card.rot { border-left:3px solid #b42318; }
.pd-ttl { font-weight:800; color:#10231f; font-size:.9rem; line-height:1.25; }
.pd-org { color:#64748b; font-size:.79rem; margin-top:1px; }
.pd-foot { display:flex; justify-content:space-between; align-items:center; margin-top:9px; }
.pd-val { font-weight:850; color:#0b3b35; font-size:.85rem; }
.pd-empty { color:#94a3b8; font-size:.8rem; padding:6px 2px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------- helpers
def esc(value):
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return html.escape(str(value))


def date_label(value):
    d = as_date(value)
    return d.strftime("%d/%m/%Y") if d else "Geen datum"


def sheet_date(value):
    """Bewaar datums als tekst voor Google Sheets/pandas, zodat afronden en uitstellen niet crasht."""
    d = as_date(value)
    return d.isoformat() if d else ""


def status_pill(status):
    kleur = STATUS_KLEUR.get(str(status), "#E5E7EB")
    return f'<span class="status-pill" style="background:{kleur};">{esc(status)}</span>'


def section(title, subtitle=""):
    st.markdown(
        f'<div class="section-title"><h2>{esc(title)}</h2>{f"<div class=\"caption2\">{esc(subtitle)}</div>" if subtitle else ""}</div>',
        unsafe_allow_html=True,
    )


def partner_options(partners):
    opts = [("", "Geen partner/installateur")]
    if len(partners):
        for _, r in partners.sort_values("bedrijf").iterrows():
            name = r.get("bedrijf") or "Naamloze partner"
            opts.append((r.get("id", ""), name))
    return opts


def customer_options(customers):
    opts = [("", "Geen bestaande klant")]
    if len(customers):
        for _, r in customers.sort_values("klant_bedrijf").iterrows():
            name = r.get("klant_bedrijf") or "Naamloze klant"
            opts.append((r.get("id", ""), name))
    return opts


def relation_options(partners, customers, projects):
    opts = [("", "", "Geen koppeling")]
    for _, r in customers.iterrows():
        opts.append(("Klant", r.get("id", ""), r.get("klant_bedrijf") or "Naamloze klant"))
    for _, r in projects.iterrows():
        opts.append(("Project", r.get("id", ""), r.get("projectnaam") or r.get("klant_bedrijf") or "Naamloos project"))
    for _, r in partners.iterrows():
        opts.append(("Partner", r.get("id", ""), r.get("bedrijf") or "Naamloze partner"))
    return opts


def workflow_hint(kind, status, today):
    suggestion = next_action_for_status(kind, status, today)
    if not suggestion.get("actie"):
        return "Deze status sluit de opvolging af. Er wordt geen nieuwe open actie gepland."
    return f"Automatisch: {suggestion['actie']} op {date_label(suggestion['datum_actie'])}."


def sync_next_action(actions_df, rel_type, rel_id, rel_name, suggestion, today, reason="Automatisch aangepast"):
    """Maak of update de open actie voor een relatie. Eindstatus zonder actie annuleert open acties."""
    df = actions_df.drop(columns=["_bucket"], errors="ignore").copy().reindex(columns=ACTION_HEADERS)
    rel_id = str(rel_id or "")
    if not rel_id:
        return df, "none"

    mask = (
        (df["relatie_type"].astype(str) == str(rel_type))
        & (df["relatie_id"].astype(str) == rel_id)
        & (df["status"].astype(str) == "Open")
    )
    actie = str(suggestion.get("actie", "") or "").strip()
    if not actie:
        if mask.any():
            df.loc[mask, "status"] = "Geannuleerd"
            df.loc[mask, "afgerond_op"] = sheet_date(today)
            df.loc[mask, "notities"] = df.loc[mask, "notities"].astype(str).str.strip() + " | Geannuleerd door statuswijziging"
            return df, "cancelled"
        return df, "none"

    datum_actie = sheet_date(as_date(suggestion.get("datum_actie")) or today + timedelta(days=7))
    prio = suggestion.get("prioriteit", "Normaal")
    kanaal = suggestion.get("kanaal", "Telefoon")
    if mask.any():
        first = df[mask].index[0]
        df.loc[first, ["relatie_naam", "actie", "datum_actie", "prioriteit", "kanaal", "notities"]] = [
            rel_name,
            actie,
            datum_actie,
            prio,
            kanaal,
            f"{reason}. Laatste update: {today.isoformat()}",
        ]
        return df, "updated"

    new_row = dict(
        id=new_id("A"),
        relatie_type=rel_type,
        relatie_id=rel_id,
        relatie_naam=rel_name,
        actie=actie,
        datum_actie=datum_actie,
        prioriteit=prio,
        status="Open",
        kanaal=kanaal,
        notities=reason,
        aangemaakt_op=sheet_date(today),
        afgerond_op="",
        cadans="",
        cadans_stap="",
    )
    df = pd.concat([df, pd.DataFrame([new_row]).reindex(columns=ACTION_HEADERS)], ignore_index=True)
    return df, "created"


def update_customer_after_project(customers_df, actions_df, project_row, today):
    """Wanneer project is uitgevoerd: klantfiche bijwerken en jaarlijkse opvolging plannen."""
    status = str(project_row.get("status") or "")
    klant_id = str(project_row.get("klant_id") or "")
    if status != "Uitgevoerd" or not klant_id or not len(customers_df):
        return customers_df, actions_df, False
    idxs = customers_df.index[customers_df["id"].astype(str) == klant_id]
    if not len(idxs):
        return customers_df, actions_df, False
    i = idxs[0]
    terugkerend = str(project_row.get("terugkerend") or customers_df.loc[i, "terugkerend"] or "Nee")
    nieuwe_status = "Terugkerende klant" if terugkerend == "Ja" else "Actieve klant"
    customers_df.loc[i, "status"] = nieuwe_status
    customers_df.loc[i, "laatste_reiniging"] = sheet_date(today)
    if terugkerend == "Ja":
        customers_df.loc[i, "volgende_contact"] = sheet_date(today + timedelta(days=330))
    suggestion = next_action_for_status("Klant", nieuwe_status, today)
    if terugkerend == "Ja":
        suggestion["datum_actie"] = sheet_date(today + timedelta(days=330))
        suggestion["actie"] = "Opnieuw contacteren voor jaarlijkse reiniging"
    customers_df.loc[i, "volgende_actie"] = suggestion["actie"]
    customers_df.loc[i, "datum_actie"] = sheet_date(suggestion["datum_actie"]) if suggestion["actie"] else ""
    actions_df, _ = sync_next_action(
        actions_df,
        "Klant",
        klant_id,
        customers_df.loc[i, "klant_bedrijf"],
        suggestion,
        today,
        "Automatisch na uitgevoerd project",
    )
    return customers_df, actions_df, True


def action_card(row):
    high = " high" if str(row.get("prioriteit")) == "Hoog" else ""
    return f"""
    <div class="nudge{' warn' if row.get('_bucket') == 'Te laat' else ' info'}">
      <div class="ic">{'⏰' if row.get('_bucket') == 'Te laat' else '✅'}</div>
      <div class="tx"><b>{esc(row.get('actie'))}</b><br>{esc(row.get('relatie_naam'))} · {esc(row.get('kanaal'))} · {date_label(row.get('datum_actie'))}</div>
    </div>
    """

def afrond_actie(actions_df, action_id, today):
    """Zet een actie op 'Gedaan', logt ze, en maakt automatisch de volgende cadansstap aan indien nodig."""
    df = actions_df.drop(columns=["_bucket"], errors="ignore").copy().reindex(columns=ACTION_HEADERS)
    idx = df.index[df["id"].astype(str) == str(action_id)]
    if len(idx) == 0:
        return None
    i = idx[0]
    df.loc[i, "status"] = "Gedaan"
    df.loc[i, "afgerond_op"] = sheet_date(today)
    row = df.loc[i].to_dict()
    volgende = cadans_volgende(row, today)
    sheets.save_actions(df)
    if volgende:
        sheets.append_action(volgende)
    soort = row.get("kanaal") if row.get("kanaal") in LOG_SOORTEN else "Notitie"
    sheets.append_log(dict(
        id=new_id("L"),
        relatie_type=row.get("relatie_type", ""),
        relatie_id=row.get("relatie_id", ""),
        relatie_naam=row.get("relatie_naam", ""),
        datum=sheet_date(today),
        soort=soort,
        notitie=f"Afgerond: {row.get('actie', '')}",
    ))
    return volgende


def snooze_actie(actions_df, action_id, dagen, today):
    """Stel een actie uit met x dagen."""
    df = actions_df.drop(columns=["_bucket"], errors="ignore").copy().reindex(columns=ACTION_HEADERS)
    idx = df.index[df["id"].astype(str) == str(action_id)]
    if len(idx) == 0:
        return
    i = idx[0]
    huidig = as_date(df.loc[i, "datum_actie"])
    basis = huidig if huidig is not None and huidig > today else today
    df.loc[i, "datum_actie"] = sheet_date(basis + timedelta(days=dagen))
    sheets.save_actions(df)


def agenda_actie_kaart(row, actions_df, today):
    """Actiekaart met afrond- en uitstelknoppen voor de Agenda."""
    high = " high" if str(row.get("prioriteit")) == "Hoog" else ""
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
    if b1.button("✓ Afronden", key=f"agenda_done_{aid}", use_container_width=True):
        volgende = afrond_actie(actions_df, aid, today)
        if volgende:
            st.toast(f"Volgende stap ingepland: {volgende['actie']} ({date_label(volgende['datum_actie'])})")
        st.rerun()
    if b2.button("+3d", key=f"agenda_sn3_{aid}", use_container_width=True):
        snooze_actie(actions_df, aid, 3, today)
        st.rerun()
    if b3.button("+7d", key=f"agenda_sn7_{aid}", use_container_width=True):
        snooze_actie(actions_df, aid, 7, today)
        st.rerun()



def to_excel_bytes(partners, customers, projects, actions, visits, log):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        partners.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Partners")
        customers.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Klanten")
        projects.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Projecten")
        actions.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Acties")
        visits.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Plaatsbezoeken")
        log.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Log")
    return buf.getvalue()


def project_board_html(projects, prijs, today):
    html_parts = ['<div class="pd-board">']
    for stage in KANBAN_STAGES:
        rows = projects[projects["status"] == stage] if len(projects) else projects
        value = sum(project_value(r, prijs) for _, r in rows.iterrows()) if len(rows) else 0
        html_parts.append(
            f'<div class="pd-col"><div class="pd-colhead"><div class="pd-stage">{esc(stage)}</div><div class="pd-sub">{len(rows)} · {euro(value)}</div></div><div class="pd-track">'
        )
        if not len(rows):
            html_parts.append('<div class="pd-empty">Geen projecten</div>')
        for _, r in rows.head(12).iterrows():
            rot = project_rotting(r, today)[0]
            html_parts.append(
                f'<div class="pd-card {"rot" if rot else ""}"><div class="pd-ttl">{esc(r.get("projectnaam"))}</div>'
                f'<div class="pd-org">{esc(r.get("klant_bedrijf"))}</div>'
                f'<div class="pd-foot"><div class="pd-val">{euro(project_value(r, prijs))}</div><div class="pd-empty">{date_label(r.get("datum_actie"))}</div></div></div>'
            )
        html_parts.append('</div></div>')
    html_parts.append('</div>')
    return "".join(html_parts)


def action_col_config():
    return {
        "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        "relatie_type": st.column_config.SelectboxColumn("Relatie type", options=["Klant", "Project", "Partner"], width="small"),
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


def customer_col_config():
    return {
        "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        "klant_bedrijf": st.column_config.TextColumn("Klant", width="medium"),
        "type": st.column_config.SelectboxColumn("Type", options=CUSTOMER_TYPES, width="small"),
        "contactpersoon": st.column_config.TextColumn("Contact", width="medium"),
        "email": st.column_config.TextColumn("E-mail", width="medium"),
        "telefoon": st.column_config.TextColumn("Telefoon", width="small"),
        "adres": st.column_config.TextColumn("Adres", width="large"),
        "regio": st.column_config.TextColumn("Regio"),
        "status": st.column_config.SelectboxColumn("Status", options=CUSTOMER_STATUSES, width="medium"),
        "terugkerend": st.column_config.SelectboxColumn("Terugkerend", options=["Nee", "Ja"], width="small"),
        "frequentie": st.column_config.SelectboxColumn("Frequentie", options=["", "Jaarlijks", "Halfjaarlijks", "Eenmalig", "Op aanvraag"], width="small"),
        "laatste_reiniging": st.column_config.DateColumn("Laatste reiniging", format="DD/MM/YYYY"),
        "volgende_contact": st.column_config.DateColumn("Volgende contact", format="DD/MM/YYYY"),
        "datum_actie": st.column_config.DateColumn("Datum actie", format="DD/MM/YYYY"),
        "notities": st.column_config.TextColumn("Notities", width="large"),
    }


def project_col_config(partners, customers):
    partner_names = [name for _, name in partner_options(partners)]
    customer_names = [name for _, name in customer_options(customers)]
    return {
        "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
        "projectnaam": st.column_config.TextColumn("Project", width="medium"),
        "klant_bedrijf": st.column_config.TextColumn("Klant", width="medium"),
        "contactpersoon": st.column_config.TextColumn("Contact", width="medium"),
        "email": st.column_config.TextColumn("E-mail", width="medium"),
        "telefoon": st.column_config.TextColumn("Telefoon", width="small"),
        "adres": st.column_config.TextColumn("Adres", width="large"),
        "regio": st.column_config.TextColumn("Regio"),
        "aantal_panelen": st.column_config.NumberColumn("# panelen", min_value=0, step=50),
        "partner_bedrijf": st.column_config.SelectboxColumn("Partner", options=partner_names, width="medium"),
        "klant_bedrijf": st.column_config.TextColumn("Klant", width="medium"),
        "bron_type": st.column_config.SelectboxColumn("Bron", options=BRON_TYPES, width="medium"),
        "status": st.column_config.SelectboxColumn("Status", options=PROJECT_STATUSES, width="medium"),
        "eerste_contact": st.column_config.DateColumn("Eerste contact", format="DD/MM/YYYY"),
        "laatste_contact": st.column_config.DateColumn("Laatste contact", format="DD/MM/YYYY"),
        "datum_actie": st.column_config.DateColumn("Datum actie", format="DD/MM/YYYY"),
        "verwachte_waarde": st.column_config.NumberColumn("Waarde", min_value=0, step=100),
        "terugkerend": st.column_config.SelectboxColumn("Terugkerend", options=["", "Nee", "Ja"], width="small"),
        "frequentie": st.column_config.SelectboxColumn("Frequentie", options=["", "Jaarlijks", "Halfjaarlijks", "Eenmalig", "Op aanvraag"], width="small"),
        "hercontactdatum": st.column_config.DateColumn("Hercontact", format="DD/MM/YYYY"),
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

# ---------------------------------------------------------------- sidebar
st.sidebar.markdown(
    """
    <div class="brand-card">
      <div class="brand-logo">🌞 Solvigo</div>
      <div class="brand-sub">CRM voor partners, klanten, projecten en opvolging</div>
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
      <strong>CRM-logica</strong><br>
      <strong>Partners</strong> brengen werk aan. <strong>Klanten</strong> zijn de bedrijven waar je reinigt. <strong>Projecten</strong> zijn concrete offertes/opdrachten. Status wijzigen past automatisch het actieblad aan.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- load
try:
    partners = sheets.load_partners()
    customers = sheets.load_customers()
    projects = sheets.load_projects()
    actions = sheets.load_actions()
    visits = sheets.load_visits()
    log = sheets.load_log()
    legacy = sheets.load_legacy_leads()
except KeyError:
    st.markdown(
        """
        <div class="hero">
            <div><p class="eyebrow">Configuratie nodig</p><h1>Solvigo CRM</h1><p>De app is gedeployed. Alleen de Streamlit Secrets ontbreken nog.</p></div>
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
weighted_pipeline = sum(weighted_value(r, prijs) for _, r in active_projects.iterrows()) if len(active_projects) else 0
rotting_rows = [r for _, r in active_projects.iterrows() if project_rotting(r, today)[0]] if len(active_projects) else []
open_project_ids = set(open_actions[open_actions["relatie_type"] == "Project"]["relatie_id"]) if len(open_actions) else set()
projects_no_action = active_projects[~active_projects["id"].isin(open_project_ids)] if len(active_projects) else active_projects

st.markdown(
    f"""
    <div class="hero">
      <div>
        <p class="eyebrow">Solvigo CRM v8.1</p>
        <h1>Partners → klanten → projecten → acties</h1>
        <p>Een installateur is een partner/bron. Een jaarlijkse eindklant is een klant. Elke offerte, reiniging of plaatsbezoek is een apart project met automatische opvolging.</p>
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

tabs = st.tabs(["📊 Dashboard", "✅ Actieblad", "🗓 Agenda", "👥 Klanten", "🏗 Projecten", "🤝 Partners", "📍 Plaatsbezoek", "🗂 Data & export"])

# ================================================================ DASHBOARD
with tabs[0]:
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Open acties", whole(len(open_actions)))
    k2.metric("Te laat", whole(len(late_actions)))
    k3.metric("Klanten", whole(len(customers)))
    k4.metric("Actieve projecten", whole(len(active_projects)))
    k5.metric("Pijplijnwaarde", euro(pipeline_value))
    k6.metric("Gewogen pijplijn", euro(weighted_pipeline), help="Waarde × winstkans per fase")

    section("Wat vraagt je aandacht?", "Automatische signalen op basis van acties en pijplijn.")
    nudges = []
    if len(late_actions):
        nudges.append(("warn", "⏰", f"<b>{len(late_actions)} acties te laat.</b> Werk ze weg in het Actieblad of de Agenda."))
    if len(today_actions):
        nudges.append(("info", "📌", f"<b>{len(today_actions)} acties vandaag.</b> Goed moment om te bellen of op te volgen."))
    if len(rotting_rows):
        namen = ", ".join(esc(r.get("projectnaam") or r.get("klant_bedrijf") or "?") for r in rotting_rows[:3])
        nudges.append(("warn", "🧊", f"<b>{len(rotting_rows)} projecten verschralen.</b> Te lang geen contact: {namen}"))
    if len(projects_no_action):
        nudges.append(("gold", "📝", f"<b>{len(projects_no_action)} actieve projecten zonder open actie.</b> Geef elk project een volgende stap."))
    if not nudges:
        st.markdown('<div class="success-card"><strong>Alles onder controle.</strong><br>Geen dringende automatische signalen.</div>', unsafe_allow_html=True)
    else:
        for cls, ic, tx in nudges:
            st.markdown(f'<div class="nudge {cls}"><div class="ic">{ic}</div><div class="tx">{tx}</div></div>', unsafe_allow_html=True)

    section("Pipeline", "Professionele opvolgflow van aanvraag tot uitvoering.")
    st.markdown(project_board_html(projects, prijs, today), unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        section("Vandaag / te laat")
        top_actions = pd.concat([late_actions, today_actions], ignore_index=True).head(8) if len(actions) else pd.DataFrame()
        if len(top_actions):
            for _, r in top_actions.iterrows():
                st.markdown(action_card(r), unsafe_allow_html=True)
        else:
            st.info("Geen acties voor vandaag of te laat.")
    with col_b:
        section("Terugkerende klanten")
        recurring = customers[customers["terugkerend"].astype(str) == "Ja"] if len(customers) else customers
        if len(recurring):
            st.dataframe(
                recurring[["klant_bedrijf", "status", "frequentie", "laatste_reiniging", "volgende_contact", "volgende_actie"]].rename(columns=LABELS),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("Nog geen terugkerende klanten aangeduid.")

# ================================================================ ACTIEBLAD
with tabs[1]:
    section("Actieblad", "Alle belacties, opvolgmailtjes, offertes en plaatsbezoeken op datum.")

    with st.expander("➕ Handmatige actie toevoegen", expanded=len(actions) == 0):
        rels = relation_options(partners, customers, projects)
        with st.form("new_action", clear_on_submit=True):
            rel_label = st.selectbox("Koppelen aan", list(range(len(rels))), format_func=lambda i: f"{rels[i][0] or 'Geen'} — {rels[i][2]}")
            rtype, rid, rname = rels[rel_label]
            c1, c2, c3 = st.columns([2, 1, 1])
            actie = c1.text_input("Actie", placeholder="Bv. offerte opvolgen / klant bellen")
            datum_actie = c2.date_input("Datum", value=today)
            prio = c3.selectbox("Prioriteit", ACTION_PRIORITIES, index=1)
            kanaal = c2.selectbox("Kanaal", ACTION_CHANNELS)
            notities = st.text_area("Notities")
            cadans = st.selectbox("Cadans optioneel", [""] + cadans_namen())
            ok = st.form_submit_button("Actie toevoegen", type="primary")
        if ok and actie.strip():
            if cadans:
                row = cadans_actie_dict(rtype or "Klant", rid, rname, cadans, 0, datum_actie, today)
                row["actie"] = actie or row["actie"]
                row["prioriteit"] = prio
                row["notities"] = notities or row["notities"]
            else:
                row = dict(id=new_id("A"), relatie_type=rtype, relatie_id=rid, relatie_naam=rname, actie=actie, datum_actie=datum_actie, prioriteit=prio, status="Open", kanaal=kanaal, notities=notities, aangemaakt_op=sheet_date(today), afgerond_op="", cadans="", cadans_stap="")
            sheets.append_action(row)
            st.success("Actie toegevoegd.")
            st.rerun()

    f1, f2, f3 = st.columns(3)
    f_status = f1.multiselect("Status", ACTION_STATUSES, default=["Open"])
    f_bucket = f2.multiselect("Timing", ["Te laat", "Vandaag", "Deze week", "Later", "Geen datum", "Afgehandeld"], default=["Te laat", "Vandaag", "Deze week", "Later", "Geen datum"])
    f_type = f3.multiselect("Relatie", ["Klant", "Project", "Partner"])
    view = actions.copy()
    if f_status:
        view = view[view["status"].isin(f_status)]
    if f_bucket and "_bucket" in view.columns:
        view = view[view["_bucket"].isin(f_bucket)]
    if f_type:
        view = view[view["relatie_type"].isin(f_type)]
    view = view.sort_values(["datum_actie", "prioriteit"], ascending=[True, True]) if len(view) else view

    edited_actions = st.data_editor(
        view.drop(columns=["_bucket"], errors="ignore"),
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        column_config=action_col_config(),
        key="actions_editor",
    )
    csave, _ = st.columns([1, 4])
    if csave.button("💾 Acties opslaan", type="primary", use_container_width=True):
        edited_actions = edited_actions.reindex(columns=ACTION_HEADERS)
        edited_actions["id"] = edited_actions["id"].apply(lambda x: x if str(x).strip() else new_id("A"))
        edited_actions["afgerond_op"] = edited_actions.apply(lambda r: sheet_date(today) if r.get("status") == "Gedaan" and as_date(r.get("afgerond_op")) is None else sheet_date(r.get("afgerond_op")), axis=1)
        base = actions.drop(columns=["_bucket"], errors="ignore").copy().reindex(columns=ACTION_HEADERS)
        base_idx = base.set_index("id") if len(base) else pd.DataFrame(columns=ACTION_HEADERS).set_index("id")
        base_idx.update(edited_actions.set_index("id"))
        new_rows = edited_actions[~edited_actions["id"].isin(base["id"])] if len(base) else edited_actions
        merged = pd.concat([base_idx.reset_index(), new_rows], ignore_index=True).reindex(columns=ACTION_HEADERS)
        # Automatische volgende cadansstap na afronden
        extra = []
        old_status = dict(zip(base["id"].astype(str), base["status"].astype(str))) if len(base) else {}
        for _, r in edited_actions.iterrows():
            if old_status.get(str(r.get("id"))) != "Gedaan" and r.get("status") == "Gedaan":
                nxt = cadans_volgende(r, today)
                if nxt:
                    extra.append(nxt)
        if extra:
            merged = pd.concat([merged, pd.DataFrame(extra).reindex(columns=ACTION_HEADERS)], ignore_index=True)
        sheets.save_actions(merged)
        st.success("Acties opgeslagen." + (f" {len(extra)} volgende cadansstap(pen) aangemaakt." if extra else ""))
        st.rerun()

# ================================================================ AGENDA
with tabs[2]:
    section("Agenda", "Je opvolging op een tijdlijn. Vink acties af of stel ze snel uit.")

    with st.expander("🔁 Opvolgreeks/cadans starten", expanded=len(open_actions) == 0):
        st.caption("Kies een klant, project of partner. De app plant stap 1 in. Wanneer je een stap afrondt, verschijnt automatisch de volgende stap.")
        rels = relation_options(partners, customers, projects)
        if len(rels) <= 1:
            st.info("Maak eerst een klant, project of partner aan.")
        else:
            with st.form("start_cadans", clear_on_submit=True):
                rel_index = st.selectbox(
                    "Voor wie?",
                    list(range(len(rels))),
                    format_func=lambda i: f"{rels[i][0] or 'Geen'} — {rels[i][2]}",
                    index=1 if len(rels) > 1 else 0,
                )
                c1, c2 = st.columns([2, 1])
                cadans = c1.selectbox("Opvolgreeks", cadans_namen())
                startdatum = c2.date_input("Startdatum", value=today)
                stappen = cadans_stappen(cadans)
                st.markdown(
                    "<div class='caption2'>Reeks: " +
                    " → ".join(f"{s['label']} (+{s['wacht']}d)" for s in stappen) +
                    "</div>",
                    unsafe_allow_html=True,
                )
                start = st.form_submit_button("Reeks starten", type="primary")
            if start:
                rel_type, rel_id, rel_name = rels[rel_index]
                if not rel_id:
                    st.warning("Kies een echte relatie om een cadans te starten.")
                else:
                    eerste = cadans_actie_dict(rel_type, rel_id, rel_name, cadans, 0, startdatum, today)
                    sheets.append_action(eerste)
                    st.success(f"Reeks '{cadans}' gestart voor {rel_name}. Eerste stap: {eerste['actie']} op {date_label(eerste['datum_actie'])}.")
                    st.rerun()

    section("Komende 14 dagen")
    per_dag = {}
    if len(open_actions):
        for _, r in open_actions.iterrows():
            d = as_date(r.get("datum_actie"))
            if d is not None:
                per_dag[d] = per_dag.get(d, 0) + 1
    weekdagen = ["ma", "di", "wo", "do", "vr", "za", "zo"]
    cells = ""
    late_total = sum(v for k, v in per_dag.items() if k < today)
    for n in range(14):
        d = today + timedelta(days=n)
        cnt = per_dag.get(d, 0)
        bg = "#0f766e" if cnt else "#ffffff"
        fg = "#ffffff" if cnt else "#94a3b8"
        ring = "border:2px solid #b42318;" if (n == 0 and late_total) else "border:1px solid var(--line);"
        badge = f'<div style="font-size:1.35rem;font-weight:850;color:{fg};">{cnt or "·"}</div>'
        latebadge = f'<div style="font-size:.7rem;color:#b42318;font-weight:850;">{late_total} te laat</div>' if (n == 0 and late_total) else '<div style="font-size:.7rem;">&nbsp;</div>'
        cells += (
            f'<div style="min-width:74px;background:{bg};{ring}border-radius:14px;'
            f'padding:.5rem;text-align:center;box-shadow:0 6px 16px rgba(15,34,31,.05);">'
            f'<div style="font-size:.72rem;color:{fg};text-transform:uppercase;font-weight:800;">{weekdagen[d.weekday()]}</div>'
            f'<div style="font-size:.8rem;color:{fg};font-weight:700;">{d.strftime("%d/%m")}</div>'
            f'{badge}{latebadge}</div>'
        )
    st.markdown(f'<div style="display:flex;gap:.5rem;overflow-x:auto;padding:.3rem 0 .8rem 0;">{cells}</div>', unsafe_allow_html=True)

    for titel, data in [
        ("⚠ Te laat", late_actions),
        ("Vandaag", today_actions),
        ("Deze week", week_actions),
    ]:
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


# ================================================================ KLANTEN
with tabs[3]:
    section("Klanten", "Eindklanten waar je voor werkt. Een jaarlijkse klant blijft hier staan; elk jaar maak je een nieuw project.")

    with st.expander("➕ Nieuwe klant", expanded=len(customers) == 0):
        with st.form("new_customer", clear_on_submit=True):
            c1, c2 = st.columns(2)
            klant = c1.text_input("Klant / bedrijf *")
            typ = c2.selectbox("Type", CUSTOMER_TYPES)
            contact = c1.text_input("Contactpersoon")
            email = c2.text_input("E-mail")
            tel = c1.text_input("Telefoon")
            regio = c2.text_input("Regio")
            adres = st.text_input("Adres")
            status = c1.selectbox("Status", CUSTOMER_STATUSES, index=CUSTOMER_STATUSES.index("Prospect"))
            terugkerend = c2.selectbox("Terugkerend?", ["Nee", "Ja"])
            frequentie = c1.selectbox("Frequentie", ["", "Jaarlijks", "Halfjaarlijks", "Eenmalig", "Op aanvraag"], index=1 if terugkerend == "Ja" else 0)
            bron_type = c2.selectbox("Bron", BRON_TYPES)
            p_opts = partner_options(partners)
            p_names = [x[1] for x in p_opts]
            p_label = c1.selectbox("Partner / doorverwijzer", p_names)
            p_id = p_opts[p_names.index(p_label)][0]
            auto_actie = st.checkbox("Volgende actie automatisch volgens status", value=True)
            st.caption(workflow_hint("Klant", status, today))
            notities = st.text_area("Notities")
            ok = st.form_submit_button("Klant toevoegen", type="primary")
        if ok and klant.strip():
            cid = new_id("K")
            suggestion = next_action_for_status("Klant", status, today) if auto_actie else {"actie": "", "datum_actie": "", "prioriteit": "Normaal", "kanaal": "Telefoon"}
            row = dict(
                id=cid, klant_bedrijf=klant, type=typ, contactpersoon=contact, email=email, telefoon=tel, adres=adres, regio=regio,
                status=status, bron_type=bron_type, partner_id=p_id, partner_bedrijf="" if p_label == "Geen partner/installateur" else p_label,
                terugkerend=terugkerend, frequentie=frequentie, laatste_reiniging="", volgende_contact="",
                laatste_contact="", volgende_actie=suggestion["actie"], datum_actie=suggestion["datum_actie"] if suggestion["actie"] else "", notities=notities,
            )
            sheets.append_customer(row)
            if suggestion["actie"]:
                sheets.append_action(dict(id=new_id("A"), relatie_type="Klant", relatie_id=cid, relatie_naam=klant, actie=suggestion["actie"], datum_actie=suggestion["datum_actie"], prioriteit=suggestion["prioriteit"], status="Open", kanaal=suggestion["kanaal"], notities="Automatisch aangemaakt bij nieuwe klant", aangemaakt_op=sheet_date(today), afgerond_op="", cadans="", cadans_stap=""))
            sheets.append_log(dict(id=new_id("L"), relatie_type="Klant", relatie_id=cid, relatie_naam=klant, datum=sheet_date(today), soort="Notitie", notitie="Nieuwe klant aangemaakt."))
            st.success("Klant toegevoegd.")
            st.rerun()

    f1, f2 = st.columns(2)
    f_status = f1.multiselect("Klantstatus", CUSTOMER_STATUSES)
    f_rec = f2.multiselect("Terugkerend", ["Ja", "Nee"])
    view = customers.copy()
    if f_status:
        view = view[view["status"].isin(f_status)]
    if f_rec:
        view = view[view["terugkerend"].isin(f_rec)]
    auto_customer_table = st.checkbox("Bij klantstatus automatisch volgende actie + actieblad aanpassen", value=True)
    edited_customers = st.data_editor(
        view,
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        column_config=customer_col_config(),
        key="customers_editor",
    )
    if st.button("💾 Klanten opslaan", type="primary", use_container_width=True):
        edited_customers = edited_customers.reindex(columns=CUSTOMER_HEADERS)
        edited_customers["id"] = edited_customers["id"].apply(lambda x: x if str(x).strip() else new_id("K"))
        base = customers.copy().reindex(columns=CUSTOMER_HEADERS)
        old_status = dict(zip(base["id"].astype(str), base["status"].astype(str))) if len(base) else {}
        base_idx = base.set_index("id") if len(base) else pd.DataFrame(columns=CUSTOMER_HEADERS).set_index("id")
        base_idx.update(edited_customers.set_index("id"))
        new_rows = edited_customers[~edited_customers["id"].isin(base["id"])] if len(base) else edited_customers
        merged = pd.concat([base_idx.reset_index(), new_rows], ignore_index=True).reindex(columns=CUSTOMER_HEADERS)
        actions_work = actions.drop(columns=["_bucket"], errors="ignore").copy().reindex(columns=ACTION_HEADERS)
        changed = 0
        if auto_customer_table:
            for _, r in edited_customers.iterrows():
                cid = str(r.get("id") or "")
                new_status = str(r.get("status") or "")
                if old_status.get(cid) != new_status:
                    idxs = merged.index[merged["id"].astype(str) == cid]
                    if not len(idxs):
                        continue
                    i = idxs[0]
                    suggestion = next_action_for_status("Klant", new_status, today)
                    if str(merged.loc[i, "terugkerend"]) == "Ja" and new_status == "Terugkerende klant":
                        suggestion["datum_actie"] = sheet_date(as_date(merged.loc[i, "volgende_contact"]) or today + timedelta(days=330))
                    merged.loc[i, "volgende_actie"] = suggestion["actie"]
                    merged.loc[i, "datum_actie"] = suggestion["datum_actie"] if suggestion["actie"] else ""
                    actions_work, _ = sync_next_action(actions_work, "Klant", cid, merged.loc[i, "klant_bedrijf"], suggestion, today, f"Automatisch aangepast door klantstatus: {old_status.get(cid) or 'nieuw'} → {new_status}")
                    changed += 1
        sheets.save_customers(merged)
        if auto_customer_table:
            sheets.save_actions(actions_work)
        st.success(f"Klanten opgeslagen. {changed} automatische opvolging(en) aangepast.")
        st.rerun()

    st.divider()
    section("Klantfiche")
    if len(customers):
        selected = st.selectbox("Kies klant", customers["id"].tolist(), format_func=lambda i: customers.loc[customers["id"] == i, "klant_bedrijf"].iloc[0] or "Naamloze klant")
        row = customers[customers["id"] == selected].iloc[0].to_dict()
        left, right = st.columns([3, 1.3])
        with left:
            st.markdown(f"### {esc(row.get('klant_bedrijf'))}", unsafe_allow_html=True)
            st.markdown(status_pill(row.get("status")), unsafe_allow_html=True)
            linked_projects = projects[projects["klant_id"].astype(str) == str(selected)] if len(projects) else projects
            st.write(f"**Contact:** {row.get('contactpersoon') or '—'} · {row.get('email') or '—'} · {row.get('telefoon') or '—'}")
            st.write(f"**Adres:** {row.get('adres') or '—'}")
            st.write(f"**Terugkerend:** {row.get('terugkerend') or 'Nee'} · {row.get('frequentie') or '—'}")
            if len(linked_projects):
                st.dataframe(linked_projects[["projectnaam", "status", "aantal_panelen", "volgende_actie", "datum_actie"]].rename(columns=LABELS), hide_index=True, use_container_width=True)
            else:
                st.info("Nog geen projecten gekoppeld aan deze klant.")
        with right:
            st.metric("Projecten", whole(len(linked_projects)))
            st.metric("Laatste reiniging", date_label(row.get("laatste_reiniging")))
            st.metric("Volgende contact", date_label(row.get("volgende_contact")))

        with st.expander("➕ Nieuw project voor deze klant"):
            with st.form("project_from_customer", clear_on_submit=True):
                c1, c2 = st.columns(2)
                projectnaam = c1.text_input("Projectnaam", value=f"Reiniging {row.get('klant_bedrijf')} {today.year}")
                panelen = c2.number_input("Aantal panelen", min_value=0, step=50, value=0, key="cust_project_panelen")
                status = c1.selectbox("Status", PROJECT_STATUSES, index=PROJECT_STATUSES.index("Nieuwe aanvraag"), key="cust_project_status")
                bron_type = c2.selectbox("Bron", BRON_TYPES, index=BRON_TYPES.index("Bestaande klant") if "Bestaande klant" in BRON_TYPES else 0, key="cust_project_bron")
                terugkerend = c1.selectbox("Terugkerend", ["", "Nee", "Ja"], index=2 if row.get("terugkerend") == "Ja" else 0, key="cust_proj_terug")
                frequentie = c2.selectbox("Frequentie", ["", "Jaarlijks", "Halfjaarlijks", "Eenmalig", "Op aanvraag"], index=1 if row.get("frequentie") == "Jaarlijks" else 0, key="cust_proj_freq")
                waarde = c1.number_input("Verwachte waarde (€)", min_value=0.0, step=100.0, value=0.0, key="cust_proj_waarde")
                auto_actie = st.checkbox("Volgende actie automatisch volgens status", value=True, key="cust_proj_auto")
                st.caption(workflow_hint("Project", status, today))
                notities = st.text_area("Notities")
                ok = st.form_submit_button("Project aanmaken", type="primary")
            if ok and projectnaam.strip():
                pid = new_id("P")
                suggestion = next_action_for_status("Project", status, today) if auto_actie else {"actie": "", "datum_actie": "", "prioriteit": "Normaal", "kanaal": "Telefoon"}
                sheets.append_project(dict(id=pid, projectnaam=projectnaam, klant_bedrijf=row.get("klant_bedrijf"), contactpersoon=row.get("contactpersoon"), email=row.get("email"), telefoon=row.get("telefoon"), adres=row.get("adres"), regio=row.get("regio"), aantal_panelen=panelen, partner_id=row.get("partner_id"), partner_bedrijf=row.get("partner_bedrijf"), bron_type=bron_type, status=status, eerste_contact="", laatste_contact="", volgende_actie=suggestion["actie"], datum_actie=suggestion["datum_actie"] if suggestion["actie"] else "", verwachte_waarde=waarde, notities=notities, klant_id=selected, terugkerend=terugkerend, frequentie=frequentie, hercontactdatum=""))
                if suggestion["actie"]:
                    sheets.append_action(dict(id=new_id("A"), relatie_type="Project", relatie_id=pid, relatie_naam=projectnaam, actie=suggestion["actie"], datum_actie=suggestion["datum_actie"], prioriteit=suggestion["prioriteit"], status="Open", kanaal=suggestion["kanaal"], notities="Automatisch aangemaakt bij nieuw project", aangemaakt_op=sheet_date(today), afgerond_op="", cadans="", cadans_stap=""))
                sheets.append_log(dict(id=new_id("L"), relatie_type="Klant", relatie_id=selected, relatie_naam=row.get("klant_bedrijf"), datum=sheet_date(today), soort="Notitie", notitie=f"Nieuw project aangemaakt: {projectnaam}."))
                st.success("Project aangemaakt.")
                st.rerun()
    else:
        st.info("Nog geen klanten.")

# ================================================================ PROJECTEN
with tabs[4]:
    section("Projecten", "Concrete offertes, plaatsbezoeken of reinigingen. Status wijzigen maakt automatisch de juiste volgende actie.")
    section("Pipeline")
    st.markdown(project_board_html(projects, prijs, today), unsafe_allow_html=True)

    with st.expander("➕ Nieuw project", expanded=len(projects) == 0):
        with st.form("new_project", clear_on_submit=True):
            c1, c2 = st.columns(2)
            cust_opts = customer_options(customers)
            cust_names = [x[1] for x in cust_opts]
            cust_label = c1.selectbox("Klant koppelen", cust_names)
            cust_id = cust_opts[cust_names.index(cust_label)][0]
            cust_row = customers[customers["id"] == cust_id].iloc[0].to_dict() if cust_id and len(customers[customers["id"] == cust_id]) else {}
            projectnaam = c1.text_input("Projectnaam *", value=f"Reiniging {cust_row.get('klant_bedrijf', '')} {today.year}" if cust_row else "")
            klant = c2.text_input("Klantbedrijf", value=cust_row.get("klant_bedrijf", ""))
            contact = c1.text_input("Contactpersoon", value=cust_row.get("contactpersoon", ""))
            email = c2.text_input("E-mail", value=cust_row.get("email", ""))
            tel = c1.text_input("Telefoon", value=cust_row.get("telefoon", ""))
            adres = c2.text_input("Adres", value=cust_row.get("adres", ""))
            regio = c1.text_input("Regio", value=cust_row.get("regio", ""))
            panelen = c2.number_input("Aantal panelen", min_value=0, step=50, value=0)
            p_opts = partner_options(partners)
            p_names = [x[1] for x in p_opts]
            p_label = c1.selectbox("Partner", p_names, index=p_names.index(cust_row.get("partner_bedrijf")) if cust_row.get("partner_bedrijf") in p_names else 0)
            p_id = p_opts[p_names.index(p_label)][0]
            bron_type = c2.selectbox("Bron", BRON_TYPES, index=BRON_TYPES.index(cust_row.get("bron_type")) if cust_row.get("bron_type") in BRON_TYPES else 0)
            status = c1.selectbox("Status", PROJECT_STATUSES, index=PROJECT_STATUSES.index("Nieuwe aanvraag"))
            waarde = c2.number_input("Verwachte waarde (€)", min_value=0.0, step=100.0, value=0.0)
            terugkerend = c1.selectbox("Terugkerend", ["", "Nee", "Ja"], index=2 if cust_row.get("terugkerend") == "Ja" else 0)
            frequentie = c2.selectbox("Frequentie", ["", "Jaarlijks", "Halfjaarlijks", "Eenmalig", "Op aanvraag"], index=1 if cust_row.get("frequentie") == "Jaarlijks" else 0)
            auto_actie = st.checkbox("Volgende actie automatisch volgens status", value=True)
            st.caption(workflow_hint("Project", status, today))
            notities = st.text_area("Notities")
            ok = st.form_submit_button("Project toevoegen", type="primary")
        if ok and projectnaam.strip():
            pid = new_id("P")
            suggestion = next_action_for_status("Project", status, today) if auto_actie else {"actie": "", "datum_actie": "", "prioriteit": "Normaal", "kanaal": "Telefoon"}
            sheets.append_project(dict(id=pid, projectnaam=projectnaam, klant_bedrijf=klant, contactpersoon=contact, email=email, telefoon=tel, adres=adres, regio=regio, aantal_panelen=panelen, partner_id=p_id, partner_bedrijf="" if p_label == "Geen partner/installateur" else p_label, bron_type=bron_type, status=status, eerste_contact="", laatste_contact="", volgende_actie=suggestion["actie"], datum_actie=suggestion["datum_actie"] if suggestion["actie"] else "", verwachte_waarde=waarde, notities=notities, klant_id=cust_id, terugkerend=terugkerend, frequentie=frequentie, hercontactdatum=""))
            if suggestion["actie"]:
                sheets.append_action(dict(id=new_id("A"), relatie_type="Project", relatie_id=pid, relatie_naam=projectnaam, actie=suggestion["actie"], datum_actie=suggestion["datum_actie"], prioriteit=suggestion["prioriteit"], status="Open", kanaal=suggestion["kanaal"], notities="Automatisch aangemaakt bij nieuw project", aangemaakt_op=sheet_date(today), afgerond_op="", cadans="", cadans_stap=""))
            st.success("Project toegevoegd.")
            st.rerun()

    f1, f2, f3 = st.columns(3)
    f_status = f1.multiselect("Status", PROJECT_STATUSES)
    f_customer = f2.text_input("Zoek klant/project")
    f_partner = f3.text_input("Zoek partner")
    view = projects.copy()
    if f_status:
        view = view[view["status"].isin(f_status)]
    if f_customer:
        s = f_customer.lower()
        view = view[view["projectnaam"].str.lower().str.contains(s, na=False) | view["klant_bedrijf"].str.lower().str.contains(s, na=False)]
    if f_partner:
        view = view[view["partner_bedrijf"].str.lower().str.contains(f_partner.lower(), na=False)]

    auto_project_table = st.checkbox("Bij projectstatus automatisch volgende actie + actieblad aanpassen", value=True)
    edited_projects = st.data_editor(view, hide_index=True, use_container_width=True, num_rows="dynamic", column_config=project_col_config(partners, customers), key="projects_editor")
    if st.button("💾 Projecten opslaan", type="primary", use_container_width=True):
        edited_projects = edited_projects.reindex(columns=PROJECT_HEADERS)
        edited_projects["id"] = edited_projects["id"].apply(lambda x: x if str(x).strip() else new_id("P"))
        partner_name_to_id = {name: pid for pid, name in partner_options(partners)}
        edited_projects["partner_id"] = edited_projects["partner_bedrijf"].map(partner_name_to_id).fillna(edited_projects["partner_id"])
        base = projects.copy().reindex(columns=PROJECT_HEADERS)
        old_status = dict(zip(base["id"].astype(str), base["status"].astype(str))) if len(base) else {}
        base_idx = base.set_index("id") if len(base) else pd.DataFrame(columns=PROJECT_HEADERS).set_index("id")
        base_idx.update(edited_projects.set_index("id"))
        new_rows = edited_projects[~edited_projects["id"].isin(base["id"])] if len(base) else edited_projects
        merged = pd.concat([base_idx.reset_index(), new_rows], ignore_index=True).reindex(columns=PROJECT_HEADERS)
        actions_work = actions.drop(columns=["_bucket"], errors="ignore").copy().reindex(columns=ACTION_HEADERS)
        customers_work = customers.copy().reindex(columns=CUSTOMER_HEADERS)
        changed = 0
        if auto_project_table:
            for _, rr in edited_projects.iterrows():
                pid = str(rr.get("id") or "")
                new_status = str(rr.get("status") or "")
                if old_status.get(pid) != new_status:
                    idxs = merged.index[merged["id"].astype(str) == pid]
                    if not len(idxs):
                        continue
                    i = idxs[0]
                    suggestion = next_action_for_status("Project", new_status, today)
                    merged.loc[i, "volgende_actie"] = suggestion["actie"]
                    merged.loc[i, "datum_actie"] = suggestion["datum_actie"] if suggestion["actie"] else ""
                    rel_name = merged.loc[i, "projectnaam"] or merged.loc[i, "klant_bedrijf"] or "Naamloos project"
                    actions_work, _ = sync_next_action(actions_work, "Project", pid, rel_name, suggestion, today, f"Automatisch aangepast door projectstatus: {old_status.get(pid) or 'nieuw'} → {new_status}")
                    customers_work, actions_work, _ = update_customer_after_project(customers_work, actions_work, merged.loc[i].to_dict(), today)
                    sheets.append_log(dict(id=new_id("L"), relatie_type="Project", relatie_id=pid, relatie_naam=rel_name, datum=sheet_date(today), soort="Notitie", notitie=f"Status gewijzigd: {old_status.get(pid) or 'nieuw'} → {new_status}. Volgende actie: {suggestion['actie'] or 'geen'}."))
                    changed += 1
        sheets.save_projects(merged)
        if auto_project_table:
            sheets.save_actions(actions_work)
            sheets.save_customers(customers_work)
        st.success(f"Projecten opgeslagen. {changed} automatische opvolging(en) aangepast.")
        st.rerun()

    st.divider()
    section("Projectfiche")
    if len(projects):
        selected = st.selectbox("Kies project", projects["id"].tolist(), format_func=lambda i: projects.loc[projects["id"] == i, "projectnaam"].iloc[0] or "Naamloos project")
        row = projects[projects["id"] == selected].iloc[0].to_dict()
        left, right = st.columns([3, 1.35])
        with left:
            st.markdown(f"### {esc(row.get('projectnaam'))}", unsafe_allow_html=True)
            with st.form("edit_project"):
                c1, c2 = st.columns(2)
                projectnaam = c1.text_input("Projectnaam", row.get("projectnaam", ""))
                klant = c2.text_input("Klantbedrijf", row.get("klant_bedrijf", ""))
                contact = c1.text_input("Contactpersoon", row.get("contactpersoon", ""))
                email = c2.text_input("E-mail", row.get("email", ""))
                tel = c1.text_input("Telefoon", row.get("telefoon", ""))
                adres = c2.text_input("Adres", row.get("adres", ""))
                regio = c1.text_input("Regio", row.get("regio", ""))
                panelen = c2.number_input("Aantal panelen", min_value=0, step=50, value=int(row.get("aantal_panelen") or 0), key="edit_proj_panelen")
                cust_opts = customer_options(customers)
                cust_names = [x[1] for x in cust_opts]
                current_customer = row.get("klant_bedrijf") if row.get("klant_id") else "Geen bestaande klant"
                cust_label = c1.selectbox("Klant koppelen", cust_names, index=cust_names.index(current_customer) if current_customer in cust_names else 0, key="edit_proj_customer")
                cust_id = cust_opts[cust_names.index(cust_label)][0]
                p_opts = partner_options(partners)
                p_names = [x[1] for x in p_opts]
                current_partner = row.get("partner_bedrijf") or "Geen partner/installateur"
                p_label = c2.selectbox("Partner", p_names, index=p_names.index(current_partner) if current_partner in p_names else 0, key="edit_proj_partner")
                p_id = p_opts[p_names.index(p_label)][0]
                bron_type = c1.selectbox("Bron", BRON_TYPES, index=BRON_TYPES.index(row.get("bron_type")) if row.get("bron_type") in BRON_TYPES else 0)
                status = c2.selectbox("Status", PROJECT_STATUSES, index=PROJECT_STATUSES.index(row.get("status")) if row.get("status") in PROJECT_STATUSES else 0)
                waarde = c1.number_input("Verwachte waarde (€)", min_value=0.0, step=100.0, value=float(row.get("verwachte_waarde") or 0), key="edit_proj_value")
                terugkerend = c2.selectbox("Terugkerend", ["", "Nee", "Ja"], index=["", "Nee", "Ja"].index(row.get("terugkerend")) if row.get("terugkerend") in ["", "Nee", "Ja"] else 0)
                frequentie = c1.selectbox("Frequentie", ["", "Jaarlijks", "Halfjaarlijks", "Eenmalig", "Op aanvraag"], index=["", "Jaarlijks", "Halfjaarlijks", "Eenmalig", "Op aanvraag"].index(row.get("frequentie")) if row.get("frequentie") in ["", "Jaarlijks", "Halfjaarlijks", "Eenmalig", "Op aanvraag"] else 0)
                auto_actie = st.checkbox("Volgende actie automatisch aanpassen volgens gekozen status", value=False, key=f"edit_project_auto_{selected}")
                suggestion = next_action_for_status("Project", status, today)
                st.caption(workflow_hint("Project", status, today))
                if auto_actie:
                    actie = c1.text_input("Volgende actie", value=suggestion["actie"], disabled=True)
                    datum_actie = c2.date_input("Datum actie", value=suggestion["datum_actie"], disabled=True, key="edit_project_date_auto")
                else:
                    actie = c1.text_input("Volgende actie", row.get("volgende_actie", ""))
                    datum_actie = c2.date_input("Datum actie", value=as_date(row.get("datum_actie")) or today + timedelta(days=7), key="edit_project_date")
                notities = st.text_area("Notities", row.get("notities", ""))
                ok = st.form_submit_button("Project opslaan", type="primary")
            if ok:
                full = projects.copy().reindex(columns=PROJECT_HEADERS)
                idx = full.index[full["id"] == selected][0]
                full.loc[idx, PROJECT_HEADERS] = [selected, projectnaam, klant, contact, email, tel, adres, regio, panelen, p_id, "" if p_label == "Geen partner/installateur" else p_label, bron_type, status, row.get("eerste_contact", ""), row.get("laatste_contact", ""), actie, datum_actie, waarde, notities, cust_id, terugkerend, frequentie, row.get("hercontactdatum", "")]
                actions_work = actions.drop(columns=["_bucket"], errors="ignore").copy().reindex(columns=ACTION_HEADERS)
                customers_work = customers.copy().reindex(columns=CUSTOMER_HEADERS)
                if auto_actie:
                    full.loc[idx, "volgende_actie"] = suggestion["actie"]
                    full.loc[idx, "datum_actie"] = suggestion["datum_actie"] if suggestion["actie"] else ""
                    actions_work, _ = sync_next_action(actions_work, "Project", selected, projectnaam, suggestion, today, f"Automatisch aangepast vanuit projectfiche door status: {row.get('status', '')} → {status}")
                    customers_work, actions_work, _ = update_customer_after_project(customers_work, actions_work, full.loc[idx].to_dict(), today)
                    sheets.save_actions(actions_work)
                    sheets.save_customers(customers_work)
                    sheets.append_log(dict(id=new_id("L"), relatie_type="Project", relatie_id=selected, relatie_naam=projectnaam, datum=sheet_date(today), soort="Notitie", notitie=f"Status opgeslagen: {row.get('status', '')} → {status}. Volgende actie: {suggestion['actie'] or 'geen'}."))
                sheets.save_projects(full)
                st.success("Project opgeslagen en opvolging bijgewerkt." if auto_actie else "Project opgeslagen.")
                st.rerun()
        with right:
            st.metric("Geschatte waarde", euro(project_value(row, prijs)))
            st.caption(f"{whole(row.get('aantal_panelen'))} panelen × € {prijs:.2f}, of ingevulde waarde")
            st.markdown(status_pill(row.get("status")), unsafe_allow_html=True)
            st.markdown("#### Offertebrug")
            st.text_area("Kopieer naar offerte-tool", offerte_tekst_project(row, prijs), height=245)
    else:
        st.info("Nog geen projecten.")

# ================================================================ PARTNERS
with tabs[5]:
    section("Partners / installateurs", "Installateurs en O&M-partijen zijn bronnen van projecten. Ze zijn geen eindklant tenzij ze zelf een reiniging afnemen.")

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
            status = c1.selectbox("Status", PARTNER_STATUSES, index=PARTNER_STATUSES.index("Te contacteren"))
            bron = c2.text_input("Bron", placeholder="Google Maps, netwerk, LinkedIn...")
            auto_actie = st.checkbox("Volgende actie automatisch volgens status", value=True, key="new_partner_auto")
            st.caption(workflow_hint("Partner", status, today))
            notities = st.text_area("Notities")
            ok = st.form_submit_button("Partner toevoegen", type="primary")
        if ok and bedrijf.strip():
            pid = new_id("R")
            suggestion = next_action_for_status("Partner", status, today) if auto_actie else {"actie": "", "datum_actie": "", "prioriteit": "Normaal", "kanaal": "Telefoon"}
            sheets.append_partner(dict(id=pid, bedrijf=bedrijf, type=typ, contactpersoon=contact, functie=functie, email=email, telefoon=tel, regio=regio, website=website, status=status, bron=bron, eerste_contact="", laatste_contact="", volgende_actie=suggestion["actie"], datum_actie=suggestion["datum_actie"] if suggestion["actie"] else "", notities=notities))
            if suggestion["actie"]:
                sheets.append_action(dict(id=new_id("A"), relatie_type="Partner", relatie_id=pid, relatie_naam=bedrijf, actie=suggestion["actie"], datum_actie=suggestion["datum_actie"], prioriteit=suggestion["prioriteit"], status="Open", kanaal=suggestion["kanaal"], notities="Automatisch aangemaakt bij nieuwe partner", aangemaakt_op=sheet_date(today), afgerond_op="", cadans="", cadans_stap=""))
            st.success("Partner toegevoegd.")
            st.rerun()

    f_status = st.multiselect("Partnerstatus", PARTNER_STATUSES)
    view = partners.copy()
    if f_status:
        view = view[view["status"].isin(f_status)]
    auto_partner_table = st.checkbox("Bij partnerstatus automatisch volgende actie + actieblad aanpassen", value=True)
    edited_partners = st.data_editor(view, hide_index=True, use_container_width=True, num_rows="dynamic", column_config=partner_col_config(), key="partners_editor")
    if st.button("💾 Partners opslaan", type="primary", use_container_width=True):
        edited_partners = edited_partners.reindex(columns=PARTNER_HEADERS)
        edited_partners["id"] = edited_partners["id"].apply(lambda x: x if str(x).strip() else new_id("R"))
        base = partners.copy().reindex(columns=PARTNER_HEADERS)
        old_status = dict(zip(base["id"].astype(str), base["status"].astype(str))) if len(base) else {}
        base_idx = base.set_index("id") if len(base) else pd.DataFrame(columns=PARTNER_HEADERS).set_index("id")
        base_idx.update(edited_partners.set_index("id"))
        new_rows = edited_partners[~edited_partners["id"].isin(base["id"])] if len(base) else edited_partners
        merged = pd.concat([base_idx.reset_index(), new_rows], ignore_index=True).reindex(columns=PARTNER_HEADERS)
        actions_work = actions.drop(columns=["_bucket"], errors="ignore").copy().reindex(columns=ACTION_HEADERS)
        changed = 0
        if auto_partner_table:
            for _, r in edited_partners.iterrows():
                pid = str(r.get("id") or "")
                new_status = str(r.get("status") or "")
                if old_status.get(pid) != new_status:
                    idxs = merged.index[merged["id"].astype(str) == pid]
                    if not len(idxs):
                        continue
                    i = idxs[0]
                    suggestion = next_action_for_status("Partner", new_status, today)
                    merged.loc[i, "volgende_actie"] = suggestion["actie"]
                    merged.loc[i, "datum_actie"] = suggestion["datum_actie"] if suggestion["actie"] else ""
                    actions_work, _ = sync_next_action(actions_work, "Partner", pid, merged.loc[i, "bedrijf"], suggestion, today, f"Automatisch aangepast door partnerstatus: {old_status.get(pid) or 'nieuw'} → {new_status}")
                    changed += 1
        sheets.save_partners(merged)
        if auto_partner_table:
            sheets.save_actions(actions_work)
        st.success(f"Partners opgeslagen. {changed} automatische opvolging(en) aangepast.")
        st.rerun()

    st.divider()
    section("Partnerfiche + doorverwijzing")
    if len(partners):
        selected = st.selectbox("Kies partner", partners["id"].tolist(), format_func=lambda i: partners.loc[partners["id"] == i, "bedrijf"].iloc[0] or "Naamloze partner")
        row = partners[partners["id"] == selected].iloc[0].to_dict()
        st.markdown(f"### {esc(row.get('bedrijf'))}", unsafe_allow_html=True)
        st.markdown(status_pill(row.get("status")), unsafe_allow_html=True)
        st.write(f"**Contact:** {row.get('contactpersoon') or '—'} · {row.get('email') or '—'} · {row.get('telefoon') or '—'}")
        linked_projects = projects[projects["partner_id"].astype(str) == str(selected)] if len(projects) else projects
        if len(linked_projects):
            st.dataframe(linked_projects[["projectnaam", "klant_bedrijf", "status", "aantal_panelen", "volgende_actie", "datum_actie"]].rename(columns=LABELS), hide_index=True, use_container_width=True)
        else:
            st.info("Nog geen projecten via deze partner.")

        with st.expander("➕ Doorverwezen klant/project aanmaken"):
            with st.form("referral_project", clear_on_submit=True):
                c1, c2 = st.columns(2)
                klant = c1.text_input("Klantbedrijf *")
                contact = c2.text_input("Contactpersoon")
                email = c1.text_input("E-mail")
                tel = c2.text_input("Telefoon")
                adres = c1.text_input("Adres")
                regio = c2.text_input("Regio", value=row.get("regio", ""))
                panelen = c1.number_input("Aantal panelen", min_value=0, step=50, value=0, key="ref_panelen")
                projectnaam = c2.text_input("Projectnaam", value="")
                maak_klant = st.checkbox("Ook klantfiche aanmaken", value=True)
                bron_type = "Doorverwijzing installateur" if row.get("type") == "Installateur" else "Doorverwijzing O&M"
                ok = st.form_submit_button("Doorverwijzing opslaan", type="primary")
            if ok and klant.strip():
                cid = ""
                if maak_klant:
                    cid = new_id("K")
                    sheets.append_customer(dict(id=cid, klant_bedrijf=klant, type="Bedrijf", contactpersoon=contact, email=email, telefoon=tel, adres=adres, regio=regio, status="Prospect", bron_type=bron_type, partner_id=selected, partner_bedrijf=row.get("bedrijf"), terugkerend="Nee", frequentie="", laatste_reiniging="", volgende_contact="", laatste_contact="", volgende_actie="Klant contacteren", datum_actie=sheet_date(today + timedelta(days=1)), notities=f"Doorverwezen door {row.get('bedrijf')}"))
                pid = new_id("P")
                pname = projectnaam or f"{klant} — reiniging zonnepanelen"
                suggestion = next_action_for_status("Project", "Nieuwe aanvraag", today)
                sheets.append_project(dict(id=pid, projectnaam=pname, klant_bedrijf=klant, contactpersoon=contact, email=email, telefoon=tel, adres=adres, regio=regio, aantal_panelen=panelen, partner_id=selected, partner_bedrijf=row.get("bedrijf"), bron_type=bron_type, status="Nieuwe aanvraag", eerste_contact="", laatste_contact="", volgende_actie=suggestion["actie"], datum_actie=suggestion["datum_actie"], verwachte_waarde=0, notities=f"Doorverwezen door {row.get('bedrijf')}", klant_id=cid, terugkerend="", frequentie="", hercontactdatum=""))
                sheets.append_action(dict(id=new_id("A"), relatie_type="Project", relatie_id=pid, relatie_naam=pname, actie=suggestion["actie"], datum_actie=suggestion["datum_actie"], prioriteit=suggestion["prioriteit"], status="Open", kanaal=suggestion["kanaal"], notities=f"Doorverwijzing via {row.get('bedrijf')}", aangemaakt_op=sheet_date(today), afgerond_op="", cadans="", cadans_stap=""))
                sheets.append_log(dict(id=new_id("L"), relatie_type="Partner", relatie_id=selected, relatie_naam=row.get("bedrijf"), datum=sheet_date(today), soort="Doorverwijzing", notitie=f"Doorverwijzing aangemaakt: {pname}."))
                st.success("Doorverwijzing opgeslagen als klant/project.")
                st.rerun()
    else:
        st.info("Nog geen partners.")

# ================================================================ PLAATSBEZOEK
with tabs[6]:
    section("Plaatsbezoek", "Maak een verslag per project. Foto's bewaar je als Google Drive-links.")
    st.markdown('<div class="soft-card"><strong>Foto’s</strong><br>Upload foto’s best naar Google Drive en plak de deel-links in het verslag.</div>', unsafe_allow_html=True)

    if len(projects):
        with st.expander("➕ Nieuw plaatsbezoekverslag", expanded=len(visits) == 0):
            with st.form("new_visit", clear_on_submit=True):
                project_ids = projects["id"].tolist()
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
                status_na = st.selectbox("Projectstatus na verslag", ["Verslag klaar", "Offerte maken", "Info gevraagd", "No-go"], index=0)
                suggestion = next_action_for_status("Project", status_na, today)
                st.caption(workflow_hint("Project", status_na, today))
                ok = st.form_submit_button("Verslag opslaan", type="primary")
            if ok:
                vid = new_id("V")
                sheets.append_visit(dict(id=vid, project_id=project_id, projectnaam=prow.get("projectnaam", ""), datum=datum, contact_ter_plaatse=contact_tp, adres=adres, aantal_panelen_gezien=panelen_gezien, dak_type=dak_type, helling=helling, vervuiling=vervuiling, toegang=toegang, waterpunt=waterpunt, veiligheid=veiligheid, verslag=verslag, foto_links=foto_links, volgende_actie=suggestion["actie"], datum_actie=suggestion["datum_actie"], aangemaakt_op=today))
                full = projects.copy().reindex(columns=PROJECT_HEADERS)
                idx = full.index[full["id"] == project_id][0]
                full.loc[idx, "status"] = status_na
                full.loc[idx, "laatste_contact"] = sheet_date(today)
                full.loc[idx, "volgende_actie"] = suggestion["actie"]
                full.loc[idx, "datum_actie"] = suggestion["datum_actie"] if suggestion["actie"] else ""
                actions_work = actions.drop(columns=["_bucket"], errors="ignore").copy().reindex(columns=ACTION_HEADERS)
                actions_work, _ = sync_next_action(actions_work, "Project", project_id, prow.get("projectnaam", ""), suggestion, today, "Aangemaakt vanuit plaatsbezoekverslag")
                sheets.save_projects(full)
                sheets.save_actions(actions_work)
                sheets.append_log(dict(id=new_id("L"), relatie_type="Project", relatie_id=project_id, relatie_naam=prow.get("projectnaam", ""), datum=sheet_date(today), soort="Bezoek", notitie=f"Plaatsbezoekverslag opgeslagen. Vervuiling: {vervuiling}. Toegang: {toegang}. Status: {status_na}."))
                st.success("Plaatsbezoekverslag, status en vervolgactie opgeslagen.")
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
            for link in [x.strip() for x in str(v.get("foto_links", "")).splitlines() if x.strip()]:
                st.write(link)
    else:
        st.info("Nog geen plaatsbezoekverslagen.")

# ================================================================ DATA & EXPORT
with tabs[7]:
    section("Data & export", "Exporteer alles naar Excel en migreer oude leads/projectklanten indien nodig.")
    st.download_button(
        "⬇ Exporteer volledige CRM naar Excel",
        to_excel_bytes(partners, customers, projects, actions.drop(columns=["_bucket"], errors="ignore"), visits, log),
        file_name="solvigo_crm_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    st.markdown("### Snelle migratie: klanten maken uit bestaande projecten")
    if len(projects):
        missing_customer = projects[(projects["klant_id"].astype(str) == "") & (projects["klant_bedrijf"].astype(str) != "")]
        st.caption(f"Projecten zonder klantfiche: {len(missing_customer)}")
        if st.button("Projectklanten aanmaken / koppelen", type="primary"):
            customers_work = customers.copy().reindex(columns=CUSTOMER_HEADERS)
            projects_work = projects.copy().reindex(columns=PROJECT_HEADERS)
            created = 0
            for _, pr in missing_customer.iterrows():
                name = str(pr.get("klant_bedrijf") or "").strip()
                if not name:
                    continue
                existing = customers_work[customers_work["klant_bedrijf"].str.lower() == name.lower()]
                if len(existing):
                    cid = existing.iloc[0]["id"]
                else:
                    cid = new_id("K")
                    customers_work = pd.concat([customers_work, pd.DataFrame([dict(id=cid, klant_bedrijf=name, type="Bedrijf", contactpersoon=pr.get("contactpersoon", ""), email=pr.get("email", ""), telefoon=pr.get("telefoon", ""), adres=pr.get("adres", ""), regio=pr.get("regio", ""), status="Prospect", bron_type=pr.get("bron_type", ""), partner_id=pr.get("partner_id", ""), partner_bedrijf=pr.get("partner_bedrijf", ""), terugkerend=pr.get("terugkerend", "Nee") or "Nee", frequentie=pr.get("frequentie", ""), laatste_reiniging="", volgende_contact="", laatste_contact=pr.get("laatste_contact", ""), volgende_actie="", datum_actie="", notities="Aangemaakt uit bestaand project")]).reindex(columns=CUSTOMER_HEADERS)], ignore_index=True)
                    created += 1
                projects_work.loc[projects_work["id"] == pr.get("id"), "klant_id"] = cid
            sheets.save_customers(customers_work)
            sheets.save_projects(projects_work)
            st.success(f"Klantfiches aangemaakt/gekoppeld. Nieuwe klanten: {created}.")
            st.rerun()

    st.markdown("### Logboek")
    if len(log):
        st.dataframe(log.sort_values("datum", ascending=False).rename(columns=LABELS), hide_index=True, use_container_width=True)
    else:
        st.info("Nog geen logboekitems.")

    st.markdown("### Oude Leads-tab migreren")
    if len(legacy):
        st.info(f"Ik vond {len(legacy)} oude lead(s) in tabblad 'Leads'. Je kan ze splitsen naar Partners, Klanten en Projecten. Het oude tabblad blijft bestaan als backup.")
        if st.button("Oude Leads splitsen naar Partners + Klanten + Projecten", type="primary"):
            new_partners = []
            new_customers = []
            new_projects = []
            new_actions = []
            for _, r in legacy.iterrows():
                if r.get("type") in LEGACY_PARTNER_TYPES:
                    rid = new_id("R")
                    status = "Gecontacteerd" if r.get("status") in ["Gecontacteerd", "Opvolgen", "Interesse / gesprek"] else "Nieuw"
                    new_partners.append(dict(id=rid, bedrijf=r.get("bedrijf", ""), type=r.get("type", "Installateur"), contactpersoon=r.get("contactpersoon", ""), functie=r.get("functie", ""), email=r.get("email", ""), telefoon=r.get("telefoon", ""), regio=r.get("regio", ""), website="", status=status, bron=r.get("bron", ""), eerste_contact=r.get("eerste_contact", ""), laatste_contact=r.get("laatste_contact", ""), volgende_actie=r.get("volgende_actie", ""), datum_actie=r.get("datum_actie", ""), notities=r.get("notities", "")))
                    if r.get("volgende_actie"):
                        new_actions.append(dict(id=new_id("A"), relatie_type="Partner", relatie_id=rid, relatie_naam=r.get("bedrijf", ""), actie=r.get("volgende_actie", ""), datum_actie=r.get("datum_actie", ""), prioriteit="Normaal", status="Open", kanaal="Telefoon", notities="Gemigreerd uit oude Leads-tab", aangemaakt_op=sheet_date(today), afgerond_op="", cadans="", cadans_stap=""))
                else:
                    cid = new_id("K")
                    pid = new_id("P")
                    new_customers.append(dict(id=cid, klant_bedrijf=r.get("bedrijf", ""), type="Bedrijf", contactpersoon=r.get("contactpersoon", ""), email=r.get("email", ""), telefoon=r.get("telefoon", ""), adres="", regio=r.get("regio", ""), status="Prospect", bron_type=r.get("bron", "Andere") if r.get("bron") in BRON_TYPES else "Andere", partner_id="", partner_bedrijf="", terugkerend="Nee", frequentie="", laatste_reiniging="", volgende_contact="", laatste_contact=r.get("laatste_contact", ""), volgende_actie=r.get("volgende_actie", ""), datum_actie=r.get("datum_actie", ""), notities=r.get("notities", "")))
                    new_projects.append(dict(id=pid, projectnaam=r.get("bedrijf", ""), klant_bedrijf=r.get("bedrijf", ""), contactpersoon=r.get("contactpersoon", ""), email=r.get("email", ""), telefoon=r.get("telefoon", ""), adres="", regio=r.get("regio", ""), aantal_panelen=r.get("aantal_panelen", 0), partner_id="", partner_bedrijf="", bron_type=r.get("bron", "Los project") if r.get("bron") in BRON_TYPES else "Andere", status="Nieuwe aanvraag", eerste_contact=r.get("eerste_contact", ""), laatste_contact=r.get("laatste_contact", ""), volgende_actie=r.get("volgende_actie", ""), datum_actie=r.get("datum_actie", ""), verwachte_waarde=0, notities=r.get("notities", ""), klant_id=cid, terugkerend="Nee", frequentie="", hercontactdatum=""))
                    if r.get("volgende_actie"):
                        new_actions.append(dict(id=new_id("A"), relatie_type="Project", relatie_id=pid, relatie_naam=r.get("bedrijf", ""), actie=r.get("volgende_actie", ""), datum_actie=r.get("datum_actie", ""), prioriteit="Normaal", status="Open", kanaal="Telefoon", notities="Gemigreerd uit oude Leads-tab", aangemaakt_op=sheet_date(today), afgerond_op="", cadans="", cadans_stap=""))
            if new_partners:
                sheets.save_partners(pd.concat([partners, pd.DataFrame(new_partners).reindex(columns=PARTNER_HEADERS)], ignore_index=True))
            if new_customers:
                sheets.save_customers(pd.concat([customers, pd.DataFrame(new_customers).reindex(columns=CUSTOMER_HEADERS)], ignore_index=True))
            if new_projects:
                sheets.save_projects(pd.concat([projects, pd.DataFrame(new_projects).reindex(columns=PROJECT_HEADERS)], ignore_index=True))
            if new_actions:
                actions_clean = actions.drop(columns=["_bucket"], errors="ignore")
                sheets.save_actions(pd.concat([actions_clean, pd.DataFrame(new_actions).reindex(columns=ACTION_HEADERS)], ignore_index=True))
            st.success("Migratie uitgevoerd. Je oude Leads-tab is niet verwijderd.")
            st.rerun()
    else:
        st.caption("Geen oude Leads-tab met data gevonden.")

    with st.expander("Technische tabbladen in Google Sheets"):
        st.write("De app gebruikt nu deze tabbladen:")
        st.code("Partners\nKlanten\nProjecten\nActies\nPlaatsbezoeken\nLog")
