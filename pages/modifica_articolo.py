# pages/modifica_articolo.py (CORRETTO)

import streamlit as st
# MODIFICA: Importiamo le funzioni corrette
from src.db import update_article, get_all_articles

def app():
    if "user_roles" not in st.session_state or "admin" not in st.session_state["user_roles"]:
        st.error("Non hai i permessi per accedere a questa pagina.")
        st.stop()
    
    if "articolo_selezionato" not in st.session_state:
        st.error("Nessun articolo selezionato.")
        st.stop()
        
    articolo = st.session_state.articolo_selezionato
    
    # MODIFICA: Otteniamo categorie e fornitori dal DB
    try:
        tutti_gli_articoli = get_all_articles()
        categorie = sorted(list(set(art['categoria'] for art in tutti_gli_articoli)))
        fornitori = sorted(list(set(art['fornitore'] for art in tutti_gli_articoli if art.get('fornitore'))))
    except Exception as e:
        st.error(f"Errore nel caricamento dati: {str(e)}")
        categorie, fornitori = [], []
    
    st.title(f"Modifica Articolo: {articolo['descrizione']}")
    
    with st.form("modifica_articolo_form"):
        codice = st.text_input("Codice Articolo", value=articolo['codice'], disabled=True)
        descrizione = st.text_input("Descrizione", value=articolo['descrizione'])
        unita = st.text_input("Unità di Misura", value=articolo['unita'])
        quantita_ordine = st.number_input("Quantità Ordinata", value=float(articolo['quantita_ordine']), min_value=0.0)
        url_immagine = st.text_input("URL Immagine", value=articolo.get('url', ''))
        
        # MODIFICA: Il selettore della categoria ora è qui
        cat_index = categorie.index(articolo['categoria']) if articolo.get('categoria') in categorie else 0
        categoria_selezionata = st.selectbox("Categoria", options=categorie, index=cat_index)
        
        forn_index = fornitori.index(articolo['fornitore']) if articolo.get('fornitore') in fornitori else 0
        fornitore_selezionato = st.selectbox("Fornitore", options=fornitori, index=forn_index)
        
        submit = st.form_submit_button("Salva Modifiche")
        
        if submit:
            updated_data = {
                "Articolo": codice,
                "Descrizione_articolo": descrizione,
                "Unita_di_misura": unita,
                "Quantita_in_ordine": float(quantita_ordine),
                "Quantita_Usata": int(articolo['quantita_usata']),
                "Fornitore": fornitore_selezionato,
                "categoria": categoria_selezionata,
                "url": url_immagine,
                "transazioni": articolo.get("transazioni", []) # Manteniamo le transazioni
            }
            
            result = update_article(codice, updated_data)
            
            if result["success"]:
                st.success(result["message"])
                # Aggiorna la sessione e torna ai dettagli
                st.session_state.articolo_selezionato = _map_mongo_doc_to_app_format(updated_data)
                st.switch_page("pages/dettaglio_articolo.py")
            else:
                st.error(result["message"])
    
    if st.button("Annulla"):
        st.switch_page("pages/dettaglio_articolo.py")

# Funzione helper per mappare i dati aggiornati al formato dell'app
def _map_mongo_doc_to_app_format(mongo_doc):
    return {
        "codice": mongo_doc.get("Articolo"), "descrizione": mongo_doc.get("Descrizione_articolo"),
        "unita": mongo_doc.get("Unita_di_misura"), "url": mongo_doc.get("url"),
        "quantita_usata": mongo_doc.get("Quantita_Usata"), "quantita_ordine": mongo_doc.get("Quantita_in_ordine"),
        "transazioni": mongo_doc.get("transazioni"), "categoria": mongo_doc.get("categoria"),
        "fornitore": mongo_doc.get("Fornitore")
    }

if __name__ == "__main__":
    app()