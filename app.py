"""Solvigo — Lead opvolging. Volledige standalone Streamlit-app."""
import io
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from core import sheets
from core.config import (ACTIEF, AFGEHANDELD, LABELS, LEAD_HEADERS, SOORTEN,
                         STATUSES, TYPES)
from core.logic import deal_value, new_id, offerte_tekst, opvolg

st.set_page_config(page_title="Solvigo — Lead opvolging", page_icon="🌞", layout="wide")


# ---------------------------------------------------------------- helpers
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
    for c in ["bedrijf", "contactpersoon", "functie", "telefoon", "regio",
              "bron", "volgende_actie"]:
        cfg[c] = st.column_config.TextColumn(LABELS[c])
    return cfg


def to_excel_bytes(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        df.rename(columns=LABELS).to_excel(xl, index=False, sheet_name="Leads")
    return buf.getvalue()


def seed_examples():
    today = date.today()
    rows = [
        dict(id=new_id(), bedrijf="Kempen Solar bvba", type="Installateur",
             contactpersoon="Tom Peeters", functie="Zaakvoerder",
             email="info@kempensolar.be", telefoon="014 12 34 56", regio="Herentals",
             aantal_panelen=0, bron="Google Maps", status="Gecontacteerd",
             eerste_contact=today - timedelta(days=8), laatste_contact=today - timedelta(days=8),
             volgende_actie="Bellen voor afspraak", datum_actie=today - timedelta(days=1),
             notities="1e mail gestuurd, nog geen reactie."),
        dict(id=new_id(), bedrijf="BioEnergie Geel NV", type="Eindklant industrieel",
             contactpersoon="Sofie Janssens", functie="Facility manager",
             email="s.janssens@bioenergiegeel.be", telefoon="014 98 76 54", regio="Geel",
             aantal_panelen=4200, bron="LinkedIn", status="Interesse / gesprek",
             eerste_contact=today - timedelta(days=14), laatste_contact=today - timedelta(days=3),
             volgende_actie="Offerte opmaken", datum_actie=today + timedelta(days=2),
             notities="Biogassite. Interesse in jaarcontract."),
        dict(id=new_id(), bedrijf="Zonnedak O&M", type="O&M",
             contactpersoon="Bart Willems", functie="Operations",
             email="bart@zonnedak.be", telefoon="03 456 78 90", regio="Antwerpen",
             aantal_panelen=1500, bron="Beurs", status="Offerte verstuurd",
             eerste_contact=today - timedelta(days=21), laatste_contact=today - timedelta(days=5),
             volgende_actie="Opvolgen offerte", datum_actie=today + timedelta(days=4),
             notities="Offerte 1.500 panelen verstuurd. Vraagt referenties."),
    ]
    sheets.save_leads(pd.DataFrame(rows).reindex(columns=LEAD_HEADERS))


# ---------------------------------------------------------------- sidebar
st.sidebar.title("🌞 Solvigo")
st.sidebar.caption("Lead opvolging")
prijs = st.sidebar.number_input("Richtprijs per paneel (€)", min_value=0.0,
                                value=st.session_state.get("prijs", 1.50), step=0.10)
st.session_state["prijs"] = prijs
if st.sidebar.button("🔄 Data vernieuwen"):
    sheets.load_leads.clear()
    sheets.load_log.clear()
    st.rerun()

# ---------------------------------------------------------------- laden
try:
    df = sheets.load_leads()
    log = sheets.load_log()
except KeyError:
    st.error("Secrets ontbreken. Zet `[sheet].id` en `[gcp_service_account]` in je secrets (zie README).")
    st.stop()
except Exception as e:
    st.error(f"Kan de Google Sheet niet laden: {e}")
    st.info("Heb je de sheet gedeeld met het e-mailadres van je service-account?")
    st.stop()

today = date.today()
if len(df):
    df["_opvolg"] = df.apply(lambda r: opvolg(r, today), axis=1)
else:
    df["_opvolg"] = pd.Series(dtype=str)

st.title("🌞 Solvigo — Lead opvolging")

if df.empty:
    st.info("Nog geen leads. Voeg er een toe via '➕ Nieuwe lead', of laad wat voorbeelddata.")
    if st.button("Voorbeelddata laden"):
        seed_examples()
        st.rerun()

tabs = st.tabs(["🔔 Opvolgen", "📋 Alle leads", "👤 Lead", "➕ Nieuwe lead", "📊 Dashboard"])

# ================================================================ OPVOLGEN
with tabs[0]:
    telaat = df[df["_opvolg"] == "\u26a0 Te laat"].sort_values("datum_actie")
    week = df[df["_opvolg"] == "Deze week"].sort_values("datum_actie")
    geen = df[df["_opvolg"] == "Geen datum"]

    c1, c2, c3 = st.columns(3)
    c1.metric("⚠ Te laat", len(telaat))
    c2.metric("Deze week", len(week))
    c3.metric("Zonder datum", len(geen))

    cols = ["bedrijf", "contactpersoon", "telefoon", "email", "status",
            "volgende_actie", "datum_actie", "notities"]

    st.subheader("⚠ Te laat")
    if len(telaat):
        st.dataframe(telaat[cols].rename(columns=LABELS), hide_index=True,
                     use_container_width=True)
    else:
        st.success("Niks te laat. 👍")

    st.subheader("Deze week")
    if len(week):
        st.dataframe(week[cols].rename(columns=LABELS), hide_index=True,
                     use_container_width=True)
    else:
        st.info("Geen acties gepland deze week.")

    if len(geen):
        with st.expander(f"Zonder opvolgdatum ({len(geen)})"):
            st.dataframe(geen[cols].rename(columns=LABELS), hide_index=True,
                         use_container_width=True)

# ================================================================ ALLE LEADS
with tabs[1]:
    st.caption("Bewerk direct in de tabel of voeg rijen toe onderaan. Klik daarna op **Opslaan**.")
    f1, f2, f3 = st.columns([2, 2, 3])
    f_status = f1.multiselect("Status", STATUSES)
    f_type = f2.multiselect("Type", TYPES)
    zoek = f3.text_input("Zoek (bedrijf / contact)")

    view = df.drop(columns=["_opvolg"]).copy()
    if f_status:
        view = view[view["status"].isin(f_status)]
    if f_type:
        view = view[view["type"].isin(f_type)]
    if zoek:
        m = (view["bedrijf"].str.contains(zoek, case=False, na=False) |
             view["contactpersoon"].str.contains(zoek, case=False, na=False))
        view = view[m]

    edited = st.data_editor(view, column_config=col_config(), num_rows="dynamic",
                            use_container_width=True, hide_index=True, key="editor")

    a, b, c = st.columns([1, 1, 4])
    if a.button("💾 Opslaan", type="primary"):
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
    if b.button("🔄 Vernieuwen"):
        sheets.load_leads.clear()
        st.rerun()
    c.download_button("⬇ Exporteer naar Excel", to_excel_bytes(df.drop(columns=["_opvolg"])),
                      file_name="solvigo_leads.xlsx",
                      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ================================================================ LEAD DETAIL
with tabs[2]:
    if df.empty:
        st.info("Nog geen leads.")
    else:
        keuze = st.selectbox(
            "Kies een lead",
            df["id"].tolist(),
            format_func=lambda i: df.loc[df["id"] == i, "bedrijf"].iloc[0] or "(naamloos)")
        row = df[df["id"] == keuze].iloc[0].to_dict()

        left, right = st.columns([3, 2])

        with left:
            st.subheader(row["bedrijf"] or "(naamloos)")
            with st.form("edit_lead"):
                g1, g2 = st.columns(2)
                bedrijf = g1.text_input("Bedrijf", row["bedrijf"])
                typ = g2.selectbox("Type", TYPES, index=TYPES.index(row["type"]) if row["type"] in TYPES else 0)
                contact = g1.text_input("Contact", row["contactpersoon"])
                functie = g2.text_input("Functie", row["functie"])
                email = g1.text_input("E-mail", row["email"])
                tel = g2.text_input("Telefoon", row["telefoon"])
                regio = g1.text_input("Regio", row["regio"])
                panelen = g2.number_input("Aantal panelen", min_value=0, step=50,
                                          value=int(row["aantal_panelen"] or 0))
                bron = g1.text_input("Bron", row["bron"])
                status = g2.selectbox("Status", STATUSES,
                                      index=STATUSES.index(row["status"]) if row["status"] in STATUSES else 0)
                actie = g1.text_input("Volgende actie", row["volgende_actie"])
                d_actie = g2.date_input("Datum actie",
                                        value=row["datum_actie"] if isinstance(row["datum_actie"], date) else today)
                notities = st.text_area("Notities", row["notities"])
                if st.form_submit_button("💾 Wijzigingen opslaan", type="primary"):
                    full = df.drop(columns=["_opvolg"]).copy()
                    idx = full.index[full["id"] == keuze][0]
                    full.loc[idx, ["bedrijf", "type", "contactpersoon", "functie", "email",
                                   "telefoon", "regio", "aantal_panelen", "bron", "status",
                                   "volgende_actie", "datum_actie", "notities"]] = [
                        bedrijf, typ, contact, functie, email, tel, regio, panelen, bron,
                        status, actie, d_actie, notities]
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
            st.metric("Geschatte waarde", f"€ {waarde:,.0f}")
            st.caption(f"{int(row['aantal_panelen'] or 0)} panelen × € {prijs:.2f}")

            st.markdown("**➡ Offerte-brug**")
            st.text_area("Kopieer naar je offerte-tool", offerte_tekst(row, prijs), height=170)

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
                sheets.append_log(dict(id=new_id(), lead_id=keuze, datum=today,
                                       soort=soort, notitie=notitie))
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
            st.dataframe(hist[["datum", "soort", "notitie"]].rename(columns=LABELS),
                         hide_index=True, use_container_width=True)
        else:
            st.caption("Nog geen contactmomenten gelogd.")

# ================================================================ NIEUWE LEAD
with tabs[3]:
    st.caption("Snel één lead toevoegen — ideaal onderweg.")
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
                volgende_actie=actie, datum_actie=d_actie, notities=notities))
            st.success(f"'{bedrijf}' toegevoegd.")
            st.rerun()

# ================================================================ DASHBOARD
with tabs[4]:
    actief = df[~df["status"].isin(AFGEHANDELD)]
    gewonnen = int((df["status"] == "Gewonnen").sum())
    verloren = int((df["status"] == "Verloren").sum())
    conv = gewonnen / (gewonnen + verloren) if (gewonnen + verloren) else 0
    pijplijn_waarde = deal_value(actief["aantal_panelen"].sum(), prijs)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Totaal leads", len(df))
    c2.metric("Actief", len(actief))
    c3.metric("Conversie", f"{conv:.0%}")
    c4.metric("Pijplijn­waarde", f"€ {pijplijn_waarde:,.0f}")

    st.subheader("Pipeline per status")
    counts = df["status"].value_counts().reindex(STATUSES).fillna(0).astype(int)
    st.bar_chart(counts)

    st.subheader("Panelen per fase (actief)")
    perfase = actief.groupby("status")["aantal_panelen"].sum().reindex(ACTIEF).fillna(0).astype(int)
    st.bar_chart(perfase)
