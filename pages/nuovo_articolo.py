# pages/nuovo_articolo.py (CORRETTO)

import streamlit as st
# MODIFICA: Importiamo le funzioni corrette
from src.db import add_new_article, get_all_articles

def app():
    if "user_roles" not in st.session_state or "admin" not in st.session_state["user_roles"]:
        st.error("Non hai i permessi per accedere a questa pagina.")
        st.stop()
        
    # MODIFICA: Otteniamo categorie e fornitori dal DB
    try:
        tutti_gli_articoli = get_all_articles()
        categorie = sorted(list(set(art['categoria'] for art in tutti_gli_articoli)))
        fornitori = sorted(list(set(art['fornitore'] for art in tutti_gli_articoli if art.get('fornitore'))))
    except Exception as e:
        st.error(f"Errore nel caricamento dati: {str(e)}")
        categorie, fornitori = [], []
    
    st.title("Aggiungi Nuovo Articolo")
    st.write("Inserisci i dati del nuovo articolo da aggiungere al magazzino.")
    
    fornitore_option = st.radio("Tipo Fornitore", ["Seleziona esistente", "Aggiungi nuovo"])
    
    fornitore_selezionato = ""
    if fornitore_option == "Seleziona esistente":
        if fornitori:
            fornitore_selezionato = st.selectbox("Seleziona Fornitore*", options=fornitori)
        else:
            st.warning("Nessun fornitore esistente. Inseriscine uno nuovo.")
            fornitore_selezionato = st.text_input("Nuovo Fornitore*")
    else:
        fornitore_selezionato = st.text_input("Nuovo Fornitore*")
    
    with st.form("nuovo_articolo_form"):
        codice = st.text_input("Codice Articolo*", help="Deve essere univoco")
        descrizione = st.text_input("Descrizione*")
        unita = st.text_input("Unità di Misura*", value="NR")
        quantita_ordine = st.number_input("Quantità Ordinata*", value=1.0, min_value=0.0)
        url_immagine = st.text_input("URL Immagine (opzionale)")
        categoria_selezionata = st.selectbox("Categoria*", options=categorie)
        
        st.info(f"Fornitore selezionato: {fornitore_selezionato}")
        
        submit = st.form_submit_button("Aggiungi Articolo")
        
        if submit:
            if not all([codice, descrizione, unita, categoria_selezionata, fornitore_selezionato]):
                st.error("Tutti i campi contrassegnati con * sono obbligatori.")
            else:
                new_article_data = {
                    "Articolo": codice,
                    "Descrizione_articolo": descrizione,
                    "Unita_di_misura": unita,
                    "Quantita_in_ordine": float(quantita_ordine),
                    "Quantita_Usata": 0,
                    "Fornitore": fornitore_selezionato,
                    "url": url_immagine,
                    "transazioni": []
                }
                
                result = add_new_article(new_article_data, categoria_selezionata)
                
                if result["success"]:
                    st.success(result["message"])
                    st.balloons()
                    st.switch_page("app.py")
                else:
                    st.error(result["message"])
    
    if st.button("Annulla"):
        st.switch_page("app.py")

if __name__ == "__main__":
    app()