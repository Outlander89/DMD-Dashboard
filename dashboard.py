"""
-----------------------
 DASHBOARD - TEMPLATE
-----------------------
 
 Så här gör du:
   1. Kör din analys SQL-fråga i MySQL Workbench
   2. Exportera resultatet som CSV 
   3. Spara filen i mappen  data/
   4. Byt ut filnamn, kolumner och rubriker i avsnittet  DINA ANALYSER
   5. Spara filen - sidan uppdateras av sig själv

 Starta appen med:   python -m streamlit run dashboard.py
=============================================================================
"""

import streamlit as st
import pandas as pd
import altair as alt


#------------------
# DASHBOARD Design
#-------------------
st.set_page_config(page_title="Dashboard", layout="wide")
 
# Färger - byt gärna ut
HUVUDFARG = "#0B3C5D"
ACCENT    = "#D9B310"
LJUS      = "#328CC1"
 
# CSS som styr utseendet på rubriker, nyckeltal och grafer
st.markdown(f"""
<style>
    .block-container {{ padding-top: 1.6rem; padding-bottom: 0.5rem; }}
    h1 {{ color: {HUVUDFARG}; margin-bottom: 0; }}
    [data-testid="stMetric"] {{
        background: #FFFFFF;
        border: 1px solid #E3EAEF;
        border-left: 5px solid {ACCENT};
        border-radius: 10px;
        padding: 12px 16px;
    }}
    [data-testid="stMetricLabel"] {{ color: #6B7A87; }}
    [data-testid="stMetricValue"] {{ color: {HUVUDFARG}; font-size: 1.7rem; }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF;
        border-radius: 12px;
    }}
</style>
""", unsafe_allow_html=True)
 
 
 
#-------------------------------------
# Läs in data och definiera funktioner
#-------------------------------------
 
# Läser filnamn ur mappen data
def las(filnamn):
    try:
        return pd.read_csv(f"data/{filnamn}")
    except FileNotFoundError:
        st.error(f"Hittar inte filen: data/{filnamn}")
        return pd.DataFrame()
 
# Läser en kolumn och summerar den
def summa(df, kolumn):
    return df[kolumn].sum() if kolumn in df.columns else 0
 
# Formaterar tal
def tal(varde, enhet=""):
    if not varde:
        return "–"
    return f"{varde:,.0f}".replace(",", " ") + enhet
 
 
HOJD = 210   # grafernas höjd i pixlar, sänk om allt inte får plats
 
# Stapeldiagram med stående staplar
def stapel(df, x, y, titel):
    with st.container(border=True):
        st.markdown(f"**{titel}**")
        if df.empty:
            return
        # Slår ihop raderna per kategori (behövs när "Alla" månader är valt)
        df = df.groupby(x, as_index=False)[y].sum()
        graf = alt.Chart(df).mark_bar(
            color=HUVUDFARG, cornerRadiusTopLeft=4, cornerRadiusTopRight=4
        ).encode(
            x=alt.X(x, sort="-y", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(y, title=None),
            tooltip=[x, y],
        ).properties(height=HOJD)
        st.altair_chart(graf, use_container_width=True)
 
# Stapeldiagram med liggande staplar
def liggande(df, x, y, titel):
    with st.container(border=True):
        st.markdown(f"**{titel}**")
        if df.empty:
            return
        # Slår ihop per namn och behåller de 10 största
        df = df.groupby(x, as_index=False)[y].sum().nlargest(10, y)
        graf = alt.Chart(df).mark_bar(
            color=ACCENT, cornerRadiusTopRight=4, cornerRadiusBottomRight=4
        ).encode(
            y=alt.Y(x, sort="-x", title=None,
                    axis=alt.Axis(labelOverlap=False, labelLimit=160)),
            x=alt.X(y, title=None),
            tooltip=[x, y],
        ).properties(height=HOJD)
        st.altair_chart(graf, use_container_width=True)
 
# Linjediagram, data över tid
def linje(df, x, y, titel):
    with st.container(border=True):
        st.markdown(f"**{titel}**")
        if df.empty:
            return
        graf = alt.Chart(df).mark_area(
            line={"color": LJUS}, color=LJUS, opacity=0.25
        ).encode(
            x=alt.X(f"{x}:T", title=None,
                    axis=alt.Axis(format="%d %b", labelAngle=0)),
            y=alt.Y(y, title=None),
            tooltip=[alt.Tooltip(f"{x}:T", format="%Y-%m-%d"), y],
        ).properties(height=HOJD)
        st.altair_chart(graf, use_container_width=True)
 
 
# Klickbar stapelgraf per månad - ett klick filtrerar alla andra grafer
def manadsgraf(df, y, titel):
    klick = alt.selection_point(name="klick", fields=["manad"])
    with st.container(border=True):
        st.markdown(f"**{titel}**  ·  klicka på en månad · klicka på en tom yta för att visa alla")
        if df.empty:
            return
        df = df.groupby("manad", as_index=False)[y].sum()
        graf = alt.Chart(df).mark_bar(
            color=ACCENT, cornerRadiusTopLeft=4, cornerRadiusTopRight=4
        ).encode(
            x=alt.X("manad", title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y(y, title=None),
            opacity=alt.condition(klick, alt.value(1), alt.value(0.35)),
            tooltip=["manad", y],
        ).add_params(klick).properties(height=120)
        st.altair_chart(graf, use_container_width=True,
                        on_select="rerun", key="manadsgraf")
 
 
# Läser vilken månad som är klickad i månadsgrafen
def klickad_manad():
    try:
        return st.session_state["manadsgraf"]["selection"]["klick"][0]["manad"]
    except (KeyError, IndexError, TypeError):
        return "Alla"
 
 
# ----------------------------
#  DINA ANALYSER - här byter du ut filnamn, kolumner och rubriker
# ----------------------------
 
# Läs in data - alla filer har kolumnen manad
klass    = las("intakt_per_status.csv")
status   = las("bokningar_per_status.csv")
per_dag  = las("flygningar_per_dag.csv")
toppen   = las("topp_passagerare.csv")
 
 
# Filter: månaden man klickat på i månadsgrafen - gäller ALLA grafer
alla_manader = klass            # sparas ofiltrerad, månadsgrafen ska alltid visa alla
vald = klickad_manad()
 
def valj_manad(df):
    """Behåller bara raderna för vald månad. 'Alla' ger alla rader."""
    if vald == "Alla" or "manad" not in df.columns:
        return df
    return df[df["manad"] == vald]
 
klass   = valj_manad(klass)
status  = valj_manad(status)
per_dag = valj_manad(per_dag)
toppen  = valj_manad(toppen)
 
 
# Rubrik
st.title("SAS – bokningsöversikt")
st.caption(f"Data från MySQL · {'mars–maj 2026' if vald == 'Alla' else vald}")
 
 
#  Nyckeltal: fyra stora siffror
intakt     = summa(klass, "intakt")
bokningar  = summa(klass, "antal_bokningar")
flygningar = summa(per_dag, "flygningar")
forsenade  = summa(per_dag, "forsenade")
 
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total intäkt", tal(intakt, " kr"))
k2.metric("Bokningar",    tal(bokningar))
k3.metric("Flygningar",   tal(flygningar))
k4.metric("Andel försenade", f"{forsenade / flygningar:.0%}" if flygningar else "–")
 
 
# Klickbar månadsgraf
manadsgraf(alla_manader, y="intakt", titel="Intäkt per månad")
 
 
# Rad 1: två grafer 
v, h = st.columns(2)
with v:
    stapel(klass, x="ticket_class", y="intakt", titel="Intäkt per biljettklass")
with h:
    stapel(status, x="status", y="bokningar", titel="Bokningar per flygstatus")
 
 
# Rad 2: två grafer 
v, h = st.columns(2)
with v:
    linje(per_dag, x="datum", y="flygningar", titel="Flygningar per dag")
with h:
    liggande(toppen, x="passagerare", y="spenderat", titel="Topp 10 kunder – spenderat belopp")
 
 

