# app.py

import streamlit as st

# st.title() crea un titolo grande
st.title("C'è festa in campo 🎉")

# st.write() può scrivere testo, numeri, dataframe e altro
st.write("Applicazione per gestire il cibo che entra ed esce dal furgone del segata")

# Aggiungiamo un widget interattivo
nome_utente = st.text_input("Come ti chiami?")

if nome_utente:
    st.write(f"Ciao, {nome_utente}!")