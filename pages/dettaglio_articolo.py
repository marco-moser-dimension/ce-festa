import streamlit as st
import json
import datetime
from api_manager import upload

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Dettaglio Articolo", page_icon="📦", layout="wide")

# Verifica se c'è un articolo selezionato nella sessione
if "articolo_selezionato" not in st.session_state:
    st.error("Nessun articolo selezionato. Torna alla homepage.")
    if st.button("Torna alla Homepage"):
        st.switch_page("app.py")
    st.stop()

# Verifica se l'utente è autenticato
if "username" not in st.session_state:
    # Prova a recuperare lo username dall'authenticator
    if "authentication_status" in st.session_state and st.session_state.authentication_status:
        if "username" in st.session_state:
            username = st.session_state.username
        else:
            st.warning("Sessione utente non trovata. Alcune funzionalità potrebbero essere limitate.")
            st.session_state.username = "utente_sconosciuto"

# Recupera l'articolo selezionato
articolo = st.session_state.articolo_selezionato

# --- Contenuto della pagina ---
st.title(f"Dettaglio Articolo: {articolo['descrizione']}")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Informazioni Articolo")
    st.write(f"**Codice:** {articolo['codice']}")
    st.write(f"**Unità di misura:** {articolo['unita']}")
    
    # Qui puoi aggiungere altre informazioni o funzionalità
    st.subheader("Gestione Quantità")
    
    # Form per aggiungere/rimuovere quantità
    with st.form("modifica_quantita"):
        operazione = st.radio("Operazione:", ["Aggiungi", "Rimuovi"])
        quantita = st.number_input("Quantità:", min_value=1, value=1)
        
        submit = st.form_submit_button("Conferma Operazione")
        if submit:
            # Formatta l'ora nel formato h:m:s
            ora_corrente = datetime.datetime.now().strftime("%H:%M:%S")
            
            # Ottieni lo username dell'utente corrente dalla sessione
            username = st.session_state.get("username", "utente_sconosciuto")
            
            # Determina il segno della quantità in base all'operazione
            quantita_effettiva = quantita if operazione == "Aggiungi" else -quantita
            
            # Chiama la funzione upload per registrare il movimento
            response = upload(
                articolo=articolo['codice'],
                alimento=articolo['descrizione'],
                quantità=quantita_effettiva,
                time=ora_corrente,
                referente=username
            )
            
            # Mostra il messaggio di successo
            st.success(f"Operazione completata: {operazione} {quantita} {articolo['unita']}")
            

with col2:
    st.subheader("Movimenti Recenti")
    # Qui potresti mostrare una tabella con i movimenti recenti dell'articolo
    st.info("Funzionalità in sviluppo")

# Pulsante per tornare alla homepage
if st.button("Torna alla Homepage"):
    # Rimuovi l'articolo selezionato dalla sessione
    del st.session_state.articolo_selezionato
    st.switch_page("app.py")