"""Google Sheets backend (gspread + google-auth)."""
from datetime import date

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

from .config import (DATE_COLS, LEAD_HEADERS, LOG_HEADERS, WS_LEADS, WS_LOG)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]


@st.cache_resource
def _spreadsheet():
    sheet_id = st.secrets["sheet"]["id"]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=SCOPES)
    return gspread.authorize(creds).open_by_key(sheet_id)


def _ensure_ws(name, headers):
    sh = _spreadsheet()
    try:
        ws = sh.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=name, rows=1000, cols=len(headers))
        ws.update(values=[headers], range_name="A1")
        return ws
    if ws.row_values(1) != headers:
        ws.update(values=[headers], range_name="A1")
    return ws


def _cell(v):
    if isinstance(v, date):
        return v.isoformat()
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    try:
        if pd.isna(v):
            return ""
    except (TypeError, ValueError):
        pass
    return str(v)


def _to_df(records, headers, date_cols=(), int_cols=()):
    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame(columns=headers)
    df = df.reindex(columns=headers)
    for c in date_cols:
        df[c] = pd.to_datetime(df[c], errors="coerce").dt.date
    for c in int_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    for c in headers:
        if c not in date_cols and c not in int_cols:
            df[c] = df[c].fillna("").astype(str)
    return df


# ---------------------------------------------------------------- leads
@st.cache_data(ttl=30)
def load_leads():
    ws = _ensure_ws(WS_LEADS, LEAD_HEADERS)
    records = ws.get_all_records(expected_headers=LEAD_HEADERS)
    return _to_df(records, LEAD_HEADERS, DATE_COLS, ["aantal_panelen"])


def save_leads(df):
    ws = _ensure_ws(WS_LEADS, LEAD_HEADERS)
    df = df.reindex(columns=LEAD_HEADERS)
    values = [LEAD_HEADERS] + [[_cell(df.iloc[i][c]) for c in LEAD_HEADERS]
                               for i in range(len(df))]
    ws.clear()
    ws.update(values=values, range_name="A1", value_input_option="USER_ENTERED")
    load_leads.clear()


def append_lead(row):
    ws = _ensure_ws(WS_LEADS, LEAD_HEADERS)
    ws.append_row([_cell(row.get(c, "")) for c in LEAD_HEADERS],
                  value_input_option="USER_ENTERED")
    load_leads.clear()


# ---------------------------------------------------------------- log
@st.cache_data(ttl=30)
def load_log():
    ws = _ensure_ws(WS_LOG, LOG_HEADERS)
    records = ws.get_all_records(expected_headers=LOG_HEADERS)
    return _to_df(records, LOG_HEADERS, ["datum"])


def append_log(row):
    ws = _ensure_ws(WS_LOG, LOG_HEADERS)
    ws.append_row([_cell(row.get(c, "")) for c in LOG_HEADERS],
                  value_input_option="USER_ENTERED")
    load_log.clear()


def save_log(df):
    ws = _ensure_ws(WS_LOG, LOG_HEADERS)
    df = df.reindex(columns=LOG_HEADERS)
    values = [LOG_HEADERS] + [[_cell(df.iloc[i][c]) for c in LOG_HEADERS]
                              for i in range(len(df))]
    ws.clear()
    ws.update(values=values, range_name="A1", value_input_option="USER_ENTERED")
    load_log.clear()
