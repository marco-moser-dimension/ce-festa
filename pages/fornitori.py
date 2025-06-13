# pages/fornitori.py
import streamlit as st
import os
from src.db import search_articles, get_all_articles, read_data
from utils import display_article_gallery

def app():
    # Configurazione della pagina
    st.title("Prodotti per Fornitore 🏭")
    st.write("Visualizza e filtra i prodotti in base al fornitore.")
    
    # Aggiungi un pulsante per tornare alla home
    if st.button("Torna alla Dashboard 🏠"):
        st.session_state.page = "home"
        st.rerun()
    
    # Ottieni il percorso del file JSON
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_FILE = os.path.join(BASE_DIR, 'data_con_fornitore.json')
    
    # Inizializza le variabili di stato, se non esistono
    if "search_query_fornitori" not in st.session_state:
        st.session_state.search_query_fornitori = ""
        
    if "fornitore_selezionato" not in st.session_state:
        st.session_state.fornitore_selezionato = "Tutti"
    
    # Ottieni la lista dei fornitori dal file JSON
    try:
        data = read_data(DATA_FILE)
        fornitori = set()
        
        # Estrai tutti i fornitori unici dal file JSON
        for categoria, articoli in data.items():
            for articolo in articoli:
                if "Fornitore" in articolo and articolo["Fornitore"]:
                    fornitori.add(articolo["Fornitore"])
        
        # Converti il set in lista e aggiungi l'opzione "Tutti"
        fornitori = ["Tutti"] + sorted(list(fornitori))
    except Exception as e:
        st.error(f"Errore nel caricamento dei fornitori: {str(e)}")
        fornitori = ["Tutti"]
    
    # Layout con due colonne per la ricerca e il selettore di fornitori
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Campo di ricerca
        st.text_input(
            "Cerca un articolo per descrizione...",
            key="search_query_fornitori",
            placeholder="Es. pasta, formaggio, acqua..."
        )
    
    with col2:
        # Selettore di fornitori
        st.selectbox(
            "Filtra per fornitore",
            options=fornitori,
            key="fornitore_selezionato"
        )
    
    # Filtra gli articoli in base alla query di ricerca e al fornitore selezionato
    query = st.session_state.search_query_fornitori.lower()
    fornitore = st.session_state.fornitore_selezionato
    
    # Filtra gli articoli in base alla query di ricerca e al fornitore selezionato
    if query:
        articoli_filtrati = search_articles(query, fornitore=fornitore)
    else:
        # Limitiamo a 40 articoli per default per migliorare le performance
        articoli_filtrati = get_all_articles(fornitore=fornitore)[:40]
    
    # Limita il numero di articoli visualizzati per migliorare le performance
    articoli_filtrati = articoli_filtrati[:40]
    
    # Mostra la galleria con gli articoli filtrati
    display_article_gallery(articoli_filtrati)

# Esegui l'app se questo file viene eseguito direttamente
if __name__ == "__main__":
    app()