"""Google Sheets backend (gspread + google-auth)."""
import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

from .logic import as_date
from .config import (
    ACTION_HEADERS,
    CUSTOMER_HEADERS,
    DATE_COLS,
    FLOAT_COLS,
    INT_COLS,
    LEGACY_LEAD_HEADERS,
    LOG_HEADERS,
    PARTNER_HEADERS,
    PROJECT_HEADERS,
    VISIT_HEADERS,
    WS_ACTIONS,
    WS_CUSTOMERS,
    WS_LEGACY_LEADS,
    WS_LOG,
    WS_PARTNERS,
    WS_PROJECTS,
    WS_VISITS,
)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]


@st.cache_resource
def _spreadsheet():
    sheet_id = st.secrets["sheet"]["id"]
    creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=SCOPES)
    return gspread.authorize(creds).open_by_key(sheet_id)


def _ensure_ws(name, headers):
    sh = _spreadsheet()
    try:
        ws = sh.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=name, rows=1000, cols=max(len(headers), 12))
        ws.update(values=[headers], range_name="A1")
        return ws

    current = ws.row_values(1)
    # Veilig migreren: bestaande kolommen behouden en ontbrekende nieuwe kolommen achteraan toevoegen.
    if current != headers:
        merged_headers = list(current) if current else []
        for h in headers:
            if h not in merged_headers:
                merged_headers.append(h)
        if not merged_headers:
            merged_headers = headers
        # Als de volgorde hetzelfde aantal oude kolommen heeft, herschrijven we naar de gewenste headers.
        # Voor Projecten staan nieuwe kolommen achteraan, zodat data niet verschuift.
        if set(current).issubset(set(headers)):
            merged_headers = headers
        ws.update(values=[merged_headers], range_name="A1")
    return ws


def _optional_ws(name):
    try:
        return _spreadsheet().worksheet(name)
    except gspread.WorksheetNotFound:
        return None


def _cell(v):
    d = as_date(v)
    if d is not None:
        return d.isoformat()
    if v is None:
        return ""
    try:
        if pd.isna(v):
            return ""
    except (TypeError, ValueError):
        pass
    return str(v)


def _to_df(records, headers, sheet_name):
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=headers)
    # Bestaande/extra kolommen negeren in de app, gewenste kolommen aanvullen.
    df = df.reindex(columns=headers)
    for c in DATE_COLS.get(sheet_name, []):
        parsed = pd.to_datetime(df[c], errors="coerce")
        df[c] = parsed.dt.strftime("%Y-%m-%d").fillna("").astype(str)
    for c in INT_COLS.get(sheet_name, []):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    for c in FLOAT_COLS.get(sheet_name, []):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).astype(float)
    typed_cols = set(DATE_COLS.get(sheet_name, []) + INT_COLS.get(sheet_name, []) + FLOAT_COLS.get(sheet_name, []))
    for c in headers:
        if c not in typed_cols:
            df[c] = df[c].fillna("").astype(str)
    return df


def _load(name, headers):
    ws = _ensure_ws(name, headers)
    records = ws.get_all_records()
    return _to_df(records, headers, name)


def _save(name, headers, df):
    ws = _ensure_ws(name, headers)
    df = df.reindex(columns=headers)
    values = [headers] + [[_cell(df.iloc[i][c]) for c in headers] for i in range(len(df))]
    ws.clear()
    ws.update(values=values, range_name="A1", value_input_option="USER_ENTERED")


def _append(name, headers, row):
    ws = _ensure_ws(name, headers)
    ws.append_row([_cell(row.get(c, "")) for c in headers], value_input_option="USER_ENTERED")


@st.cache_data(ttl=30)
def load_partners():
    return _load(WS_PARTNERS, PARTNER_HEADERS)


def save_partners(df):
    _save(WS_PARTNERS, PARTNER_HEADERS, df)
    load_partners.clear()


def append_partner(row):
    _append(WS_PARTNERS, PARTNER_HEADERS, row)
    load_partners.clear()


@st.cache_data(ttl=30)
def load_customers():
    return _load(WS_CUSTOMERS, CUSTOMER_HEADERS)


def save_customers(df):
    _save(WS_CUSTOMERS, CUSTOMER_HEADERS, df)
    load_customers.clear()


def append_customer(row):
    _append(WS_CUSTOMERS, CUSTOMER_HEADERS, row)
    load_customers.clear()


@st.cache_data(ttl=30)
def load_projects():
    return _load(WS_PROJECTS, PROJECT_HEADERS)


def save_projects(df):
    _save(WS_PROJECTS, PROJECT_HEADERS, df)
    load_projects.clear()


def append_project(row):
    _append(WS_PROJECTS, PROJECT_HEADERS, row)
    load_projects.clear()


@st.cache_data(ttl=30)
def load_actions():
    return _load(WS_ACTIONS, ACTION_HEADERS)


def save_actions(df):
    _save(WS_ACTIONS, ACTION_HEADERS, df)
    load_actions.clear()


def append_action(row):
    _append(WS_ACTIONS, ACTION_HEADERS, row)
    load_actions.clear()


@st.cache_data(ttl=30)
def load_visits():
    return _load(WS_VISITS, VISIT_HEADERS)


def save_visits(df):
    _save(WS_VISITS, VISIT_HEADERS, df)
    load_visits.clear()


def append_visit(row):
    _append(WS_VISITS, VISIT_HEADERS, row)
    load_visits.clear()


@st.cache_data(ttl=30)
def load_log():
    return _load(WS_LOG, LOG_HEADERS)


def save_log(df):
    _save(WS_LOG, LOG_HEADERS, df)
    load_log.clear()


def append_log(row):
    _append(WS_LOG, LOG_HEADERS, row)
    load_log.clear()


@st.cache_data(ttl=30)
def load_legacy_leads():
    ws = _optional_ws(WS_LEGACY_LEADS)
    if ws is None:
        return pd.DataFrame(columns=LEGACY_LEAD_HEADERS)
    records = ws.get_all_records()
    return _to_df(records, LEGACY_LEAD_HEADERS, WS_LEGACY_LEADS)


def clear_all_caches():
    load_partners.clear()
    load_customers.clear()
    load_projects.clear()
    load_actions.clear()
    load_visits.clear()
    load_log.clear()
    load_legacy_leads.clear()
