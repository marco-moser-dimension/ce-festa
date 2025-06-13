# app.py (Versione Semplificata, Pulita e Funzionale)

import streamlit as st
import json
import os
from pages.login import login_flow
from src.db import search_articles, get_all_articles, read_data
from utils import display_article_gallery
from pages.fornitori import app as fornitori_app

# Configurazione della pagina per massimizzare lo spazio
st.set_page_config(
    page_title="Homepage Magazzino", 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="collapsed"  # Collassa la sidebar per massimizzare lo spazio
)

# --- FLUSSO PRINCIPALE DELL'APPLICAZIONE ---

# Esegui il login. Se non va a buon fine, ferma tutto.
if not login_flow():
    st.stop()

# Inizializza le variabili di stato, se non esistono
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
    
if "categoria_selezionata" not in st.session_state:
    st.session_state.categoria_selezionata = "Tutte"
    
if "page" not in st.session_state:
    st.session_state.page = "home"

# Ottieni il percorso del file JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data_con_fornitore.json')

# Leggi il file JSON per ottenere le categorie
try:
    data = read_data(DATA_FILE)
    categorie = list(data.keys())
    # Aggiungi l'opzione "Tutte" all'inizio
    categorie = ["Tutte"] + categorie
except Exception as e:
    st.error(f"Errore nel caricamento delle categorie: {str(e)}")
    categorie = ["Tutte"]

# --- Intestazione e barra di ricerca ---
st.title("Dashboard Magazzino 📦")
st.write("Cerca un articolo o selezionalo dalla lista per vederne i dettagli.")

# Aggiungi un pulsante per navigare alla pagina dei fornitori
if st.button("Visualizza per Fornitore 🏭"):
    st.session_state.page = "fornitori"
    st.rerun()

# Controlla se siamo nella pagina dei fornitori
if st.session_state.get("page") == "fornitori":
    fornitori_app()
    st.stop()

# Layout con due colonne per la ricerca e il selettore di categorie
col1, col2 = st.columns([3, 1])

with col1:
    # Campo di ricerca
    st.text_input(
        "Cerca un articolo per descrizione...",
        key="search_query",
        placeholder="Es. pasta, formaggio, acqua..."
    )

with col2:
    # Selettore di categorie
    st.selectbox(
        "Filtra per categoria",
        options=categorie,
        key="categoria_selezionata"
    )

# Filtra gli articoli in base alla query di ricerca e alla categoria selezionata
query = st.session_state.search_query.lower()
categoria = st.session_state.categoria_selezionata

if query:
    articoli_filtrati = search_articles(query, categoria=categoria)
else:
    # Limitiamo a 40 articoli per default per migliorare le performance
    articoli_filtrati = get_all_articles(categoria=categoria)[:40]

# Mostra la galleria con gli articoli filtrati
display_article_gallery(articoli_filtrati)