# pages/fornitori.py (CORRETTO)

import streamlit as st
# MODIFICA: Importiamo solo le funzioni necessarie
from src.db import search_articles, get_all_articles
from utils import display_article_gallery

def app():
    st.title("Prodotti per Fornitore 🏭")
    st.write("Visualizza e filtra i prodotti in base al fornitore.")
    
    if st.button("Torna alla Dashboard 🏠"):
        st.session_state.page = "home"
        st.rerun()
    
    if "search_query_fornitori" not in st.session_state:
        st.session_state.search_query_fornitori = ""
    if "fornitore_selezionato" not in st.session_state:
        st.session_state.fornitore_selezionato = "Tutti"
    
    # MODIFICA: Otteniamo la lista dei fornitori dal DB
    try:
        tutti_gli_articoli = get_all_articles()
        if tutti_gli_articoli:
            fornitori_unici = sorted(list(set(
                art['fornitore'] for art in tutti_gli_articoli if art.get('fornitore')
            )))
            fornitori = ["Tutti"] + fornitori_unici
        else:
            fornitori = ["Tutti"]
    except Exception as e:
        st.error(f"Errore nel caricamento dei fornitori: {str(e)}")
        fornitori = ["Tutti"]
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Cerca un articolo...", key="search_query_fornitori")
    with col2:
        st.selectbox("Filtra per fornitore", options=fornitori, key="fornitore_selezionato")
    
    query = st.session_state.search_query_fornitori
    fornitore = st.session_state.fornitore_selezionato
    
    # MODIFICA: La logica di ricerca è gestita da search_articles
    articoli_filtrati = search_articles(query, fornitore=fornitore)
    
    display_article_gallery(articoli_filtrati)

if __name__ == "__main__":
    app()