# app.py

import streamlit as st

# st.title() crea un titolo grande
st.title("La mia prima App Streamlit! 🎉")

# st.write() può scrivere testo, numeri, dataframe e altro
st.write("Ciao mondo, questo è più facile di quanto pensassi.")

# Aggiungiamo un widget interattivo
nome_utente = st.text_input("Come ti chiami?")

if nome_utente:
    st.write(f"Ciao, {nome_utente}!")