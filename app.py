# app.py (La nuova Homepage con la Galleria)

import streamlit as st
import json
# Ora importiamo da pages.login
from pages.login import login_flow 

data_file_path = './data.json'

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Homepage Magazzino", page_icon="🏠", layout="wide")

def carica_articoli(file_path):
    """
    Carica gli articoli dal file JSON e li mappa nel formato richiesto
    """
    with open(file_path, 'r') as file:
        articoli_completi = json.load(file)
    
    # Mappa i dati nel formato richiesto
    articoli_mappati = [
        {
            "codice": articolo["Articolo"], 
            "descrizione": articolo["Descrizione articolo"],
            "unita": articolo["Unità di misura"]
        } 
        for articolo in articoli_completi[:]
    ]
    
    return articoli_mappati


# --- GESTIONE LOGIN ---
# Il login protegge TUTTA l'app. Lo mettiamo qui.
if not login_flow():
    st.stop() # Ferma l'esecuzione se l'utente non è loggato

# --- Contenuto della Homepage ---
st.title("Dashboard Magazzino 📦")
st.write("Seleziona un articolo per vedere i dettagli o aggiungerne di nuovi.")


# Carica gli articoli per la dashboard
articoli_esempio = carica_articoli(data_file_path)

# Creiamo una griglia di 3 colonne
col1, col2, col3 = st.columns(3)
colonne = [col1, col2, col3]

for i, articolo in enumerate(articoli_esempio):
    with colonne[i % 3]:
        with st.container(border=True):
            st.subheader(articolo["descrizione"])
            st.caption(f"Codice: {articolo['codice']}")
            
            # Aggiungiamo un bottone per rendere la card cliccabile
            if st.button("Visualizza dettagli", key=f"btn_{articolo['codice']}"):
                # Salva l'articolo selezionato nella sessione
                st.session_state.articolo_selezionato = articolo
                # Reindirizza alla pagina dei dettagli
                st.switch_page("pages/dettaglio_articolo.py")