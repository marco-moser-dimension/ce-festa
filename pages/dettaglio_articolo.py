import streamlit as st
import json

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Dettaglio Articolo", page_icon="📦", layout="wide")

# Verifica se c'è un articolo selezionato nella sessione
if "articolo_selezionato" not in st.session_state:
    st.error("Nessun articolo selezionato. Torna alla homepage.")
    if st.button("Torna alla Homepage"):
        st.switch_page("app.py")
    st.stop()

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
        note = st.text_area("Note:", placeholder="Inserisci eventuali note...")
        
        submit = st.form_submit_button("Conferma Operazione")
        if submit:
            # Qui implementerai la logica per aggiornare la quantità
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