# pages/modifica_articolo.py
import streamlit as st
import os
from src.db import get_article_by_code, update_article, read_data

def app():
    # Verifica che l'utente sia admin
    if "user_roles" not in st.session_state or "admin" not in st.session_state["user_roles"]:
        st.error("Non hai i permessi per accedere a questa pagina.")
        if st.button("Torna alla Dashboard"):
            st.switch_page("app.py")
        return
    
    # Verifica che ci sia un articolo selezionato
    if "articolo_selezionato" not in st.session_state:
        st.error("Nessun articolo selezionato.")
        if st.button("Torna alla Dashboard"):
            st.switch_page("app.py")
        return
        
    # Inizializza la variabile di stato per la navigazione
    if "go_to_details" not in st.session_state:
        st.session_state.go_to_details = False
    
    articolo = st.session_state.articolo_selezionato
    
    # Ottieni il percorso del file JSON
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_FILE = os.path.join(BASE_DIR, 'data_con_fornitore.json')
    
    # Leggi il file JSON per ottenere le categorie
    try:
        data = read_data(DATA_FILE)
        categorie = list(data.keys())
    except Exception as e:
        st.error(f"Errore nel caricamento delle categorie: {str(e)}")
        categorie = []
    
    # Ottieni la lista dei fornitori dal file JSON
    fornitori = set()
    try:
        for categoria, articoli in data.items():
            for art in articoli:
                if "Fornitore" in art and art["Fornitore"]:
                    fornitori.add(art["Fornitore"])
        fornitori = sorted(list(fornitori))
    except Exception as e:
        st.error(f"Errore nel caricamento dei fornitori: {str(e)}")
        fornitori = []
    
    st.title(f"Modifica Articolo: {articolo['descrizione']}")
    
    # Form per la modifica dell'articolo
    with st.form("modifica_articolo_form"):
        # Campi del form
        codice = st.text_input("Codice Articolo", value=articolo['codice'], disabled=True)
        descrizione = st.text_input("Descrizione", value=articolo['descrizione'])
        unita = st.text_input("Unità di Misura", value=articolo['unita'])
        quantita_ordine = st.number_input("Quantità Ordinata", value=float(articolo['quantita_ordine']), min_value=0.0)
        url_immagine = st.text_input("URL Immagine", value=articolo.get('url', ''))
        
        # Selettore per il fornitore
        fornitore_index = 0
        if articolo.get('fornitore') in fornitori:
            fornitore_index = fornitori.index(articolo['fornitore'])
        
        fornitore = st.selectbox("Fornitore", options=fornitori, index=fornitore_index)
        
        # Pulsante per salvare le modifiche
        submit = st.form_submit_button("Salva Modifiche")
        
        if submit:
            # Prepara i dati aggiornati
            updated_data = {
                "Articolo": codice,
                "Descrizione_articolo": descrizione,
                "Unita_di_misura": unita,
                "Quantita_in_ordine": str(quantita_ordine),
                "Quantita_Usata": str(articolo['quantita_usata']),
                "Fornitore": fornitore
            }
            
            # Aggiungi l'URL solo se è stato fornito
            if url_immagine:
                updated_data["url"] = url_immagine
            
            # Aggiorna l'articolo
            result = update_article(codice, updated_data)
            
            if result["success"]:
                st.success(result["message"])
                
                # Aggiorna l'articolo nella sessione
                updated_article = {
                    "codice": codice,
                    "descrizione": descrizione,
                    "unita": unita,
                    "quantita_ordine": float(quantita_ordine),
                    "quantita_usata": articolo['quantita_usata'],
                    "fornitore": fornitore,
                    "categoria": result.get("categoria", articolo.get("categoria", "")),
                    "transazioni": articolo.get("transazioni", [])
                }
                
                if url_immagine:
                    updated_article["url"] = url_immagine
                
                st.session_state.articolo_selezionato = updated_article
                
                # Imposta la variabile di stato per tornare alla pagina di dettaglio
                st.session_state.go_to_details = True
            else:
                st.error(result["message"])
    
    # Pulsante per tornare alla pagina di dettaglio
    if st.button("Annulla"):
        st.switch_page("pages/dettaglio_articolo.py")
        
    # Controlla se dobbiamo tornare alla pagina di dettaglio
    if st.session_state.go_to_details:
        st.switch_page("pages/dettaglio_articolo.py")

# Esegui l'app se questo file viene eseguito direttamente
if __name__ == "__main__":
    app()