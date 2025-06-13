# app.py (Versione aggiornata per MongoDB)

import streamlit as st
from pages.login import login_flow
# 1. MODIFICA: Importiamo le funzioni corrette da src.db
from src.db import search_articles, get_all_articles 
from utils import display_article_gallery
from pages.fornitori import app as fornitori_app

# Configurazione della pagina (invariata)
st.set_page_config(
    page_title="Homepage Magazzino", 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- FLUSSO PRINCIPALE DELL'APPLICAZIONE ---

# Esegui il login (invariato)
if not login_flow():
    st.stop()

# Inizializza le variabili di stato (invariato)
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "categoria_selezionata" not in st.session_state:
    st.session_state.categoria_selezionata = "Tutte"
if "page" not in st.session_state:
    st.session_state.page = "home"
if "go_to_dashboard" in st.session_state:
    st.session_state.go_to_dashboard = False
if "show_delete_confirm" in st.session_state:
    st.session_state.show_delete_confirm = False

# 2. MODIFICA: Otteniamo le categorie direttamente da MongoDB
#    Questa sezione sostituisce la lettura del file JSON.
try:
    # Chiamiamo get_all_articles senza filtri per avere tutti i dati
    tutti_gli_articoli = get_all_articles() 
    # Estraiamo le categorie uniche dai dati e le ordiniamo
    if tutti_gli_articoli:
        categorie_uniche = sorted(list(set(articolo['categoria'] for articolo in tutti_gli_articoli)))
        categorie = ["Tutte"] + categorie_uniche
    else:
        categorie = ["Tutte"]
except Exception as e:
    st.error(f"Errore nel caricamento delle categorie dal database: {str(e)}")
    categorie = ["Tutte"]

# --- Intestazione e barra di ricerca (invariato) ---
st.title("Dashboard Magazzino 📦")
st.write("Cerca un articolo o selezionalo dalla lista per vederne i dettagli.")

if st.button("Visualizza per Fornitore 🏭"):
    st.session_state.page = "fornitori"
    st.rerun()

if st.session_state.get("page") == "fornitori":
    fornitori_app()
    st.stop()

col1, col2 = st.columns([3, 1])

with col1:
    st.text_input(
        "Cerca un articolo per descrizione...",
        key="search_query",
        placeholder="Es. pasta, formaggio, acqua..."
    )

with col2:
    st.selectbox(
        "Filtra per categoria",
        options=categorie,
        key="categoria_selezionata"
    )

# 3. MODIFICA: La logica di filtraggio ora è più semplice e diretta.
#    Le funzioni search_articles e get_all_articles ora interrogano MongoDB.
query = st.session_state.search_query
categoria = st.session_state.categoria_selezionata

# La logica di ricerca e filtraggio è gestita direttamente dalle funzioni di db.py
# Non c'è più bisogno di un if/else separato.
# La funzione search_articles gestisce sia il caso con query che senza.
# NOTA: La limitazione a 40 articoli è stata rimossa, MongoDB è veloce.
# Se vuoi reintrodurla, puoi farlo dopo la chiamata alla funzione.
articoli_filtrati = search_articles(query, categoria=categoria)

# Verifica se l'utente è admin (invariato)
is_admin = False
if "user_roles" in st.session_state and "admin" in st.session_state.user_roles:
    is_admin = True
    if st.button("➕ Aggiungi Nuovo Articolo"):
        st.switch_page("pages/nuovo_articolo.py")

# Mostra la galleria con gli articoli filtrati (invariato)
display_article_gallery(articoli_filtrati)