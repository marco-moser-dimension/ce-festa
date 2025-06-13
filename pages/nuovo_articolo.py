# pages/nuovo_articolo.py
import streamlit as st
import os
from src.db import add_new_article, read_data

def app():
    # Verifica che l'utente sia admin
    if "user_roles" not in st.session_state or "admin" not in st.session_state["user_roles"]:
        st.error("Non hai i permessi per accedere a questa pagina.")
        if st.button("Torna alla Dashboard"):
            st.switch_page("app.py")
        return
        
    # Inizializza le variabili di stato
    if "go_to_dashboard" not in st.session_state:
        st.session_state.go_to_dashboard = False
    
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
            for articolo in articoli:
                if "Fornitore" in articolo and articolo["Fornitore"]:
                    fornitori.add(articolo["Fornitore"])
        fornitori = sorted(list(fornitori))
    except Exception as e:
        st.error(f"Errore nel caricamento dei fornitori: {str(e)}")
        fornitori = []
    
    st.title("Aggiungi Nuovo Articolo")
    st.write("Inserisci i dati del nuovo articolo da aggiungere al magazzino.")
    
    # Selettore per il tipo di fornitore (FUORI dal form)
    fornitore_option = st.radio("Tipo Fornitore", ["Seleziona esistente", "Aggiungi nuovo"])
    
    # Inizializza la variabile fornitore
    if "fornitore" not in st.session_state:
        st.session_state.fornitore = ""
    
    # Gestisci l'input del fornitore in base all'opzione selezionata (FUORI dal form)
    if fornitore_option == "Seleziona esistente":
        if fornitori:
            st.session_state.fornitore = st.selectbox("Seleziona Fornitore*", options=fornitori)
        else:
            st.warning("Nessun fornitore esistente. Inserisci un nuovo fornitore.")
            st.session_state.fornitore = st.text_input("Nuovo Fornitore*")
    else:
        # Campo di testo per il nuovo fornitore
        st.session_state.fornitore = st.text_input("Nuovo Fornitore*")
    
    # Form per l'aggiunta di un nuovo articolo
    with st.form("nuovo_articolo_form"):
        # Campi del form
        codice = st.text_input("Codice Articolo*", help="Deve essere univoco")
        descrizione = st.text_input("Descrizione*")
        unita = st.text_input("Unità di Misura*", value="NR")
        quantita_ordine = st.number_input("Quantità Ordinata*", value=1.0, min_value=0.0)
        url_immagine = st.text_input("URL Immagine (opzionale)")
        
        # Selettore per la categoria
        categoria = st.selectbox("Categoria*", options=categorie)
        
        # Mostra il fornitore selezionato (solo visualizzazione)
        st.info(f"Fornitore selezionato: {st.session_state.fornitore}")
        
        # Pulsante per salvare il nuovo articolo
        submit = st.form_submit_button("Aggiungi Articolo")
        
        if submit:
            # Verifica che tutti i campi obbligatori siano compilati
            if not codice or not descrizione or not unita or not categoria or not st.session_state.fornitore:
                st.error("Tutti i campi contrassegnati con * sono obbligatori.")
            else:
                # Prepara i dati del nuovo articolo
                new_article_data = {
                    "Articolo": codice,
                    "Descrizione_articolo": descrizione,
                    "Unita_di_misura": unita,
                    "Quantita_in_ordine": str(quantita_ordine),
                    "Quantita_Usata": "0",
                    "Fornitore": st.session_state.fornitore
                }
                
                # Aggiungi l'URL solo se è stato fornito
                if url_immagine:
                    new_article_data["url"] = url_immagine
                
                # Aggiungi il nuovo articolo
                result = add_new_article(new_article_data, categoria)
                
                if result["success"]:
                    st.success(result["message"])
                    # Torna alla dashboard
                    st.session_state.go_to_dashboard = True
                else:
                    st.error(result["message"])
    
    # Pulsante per tornare alla dashboard
    if st.button("Annulla"):
        st.switch_page("app.py")
        
    # Controlla se dobbiamo tornare alla dashboard
    if st.session_state.go_to_dashboard:
        st.switch_page("app.py")

# Esegui l'app se questo file viene eseguito direttamente
if __name__ == "__main__":
    app()