import streamlit as st
import pandas as pd
from dashboard import las

st.header("Analys av antal sålda biljetter per match")
st.write("Den här dashboarden visar försäljningen per match och låter dig analysera datan")

df = las("Mästerskap.csv")

st.metric("Totalt sålda biljetter", df["antal_biljetter"].sum())
st.metric("Snitt per match", round(df["antal_biljetter"].mean(), 2))

st.dataframe(df, hide_index=True)
st.bar_chart(df, x="match_id", y="antal_biljetter")




             