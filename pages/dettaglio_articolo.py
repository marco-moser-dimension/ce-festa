# pages/dettaglio_articolo.py (VERSIONE CON LAYOUT CORRETTO)

import streamlit as st
from utils import display_article_details, handle_quantity_update, display_transactions
from src.db import delete_article, get_article_by_code

st.set_page_config(page_title="Dettaglio Articolo", page_icon="📦", layout="wide")

# --- Controlli di accesso e caricamento dati ---
if "articolo_selezionato" not in st.session_state:
    st.error("Nessun articolo selezionato. Torna alla homepage.")
    if st.button("Torna alla Homepage"):
        st.switch_page("app.py")
    st.stop()

if "username" not in st.session_state:
    st.warning("Sessione utente non trovata. Alcune funzionalità potrebbero essere limitate.")
    st.session_state.username = "utente_sconosciuto"

articolo = get_article_by_code(st.session_state.articolo_selezionato['codice'])
if not articolo:
    st.error("Articolo non trovato nel database. Potrebbe essere stato eliminato.")
    st.stop()
st.session_state.articolo_selezionato = articolo

# --- Definizione del Layout Principale ---
st.title(f"Dettaglio Articolo: {articolo['descrizione']}")

# Creiamo le colonne UNA SOLA VOLTA
main_col1, main_col2 = st.columns([2, 1])

# --- Colonna Sinistra: Dettagli e Gestione Quantità ---
with main_col1:
    # Mostra i dettagli principali (senza creare nuove colonne)
    st.subheader("Informazioni Articolo")
    st.write(f"**Codice:** {articolo['codice']}")
    st.write(f"**Unità di misura:** {articolo['unita']}")
    st.write(f"**Categoria:** {articolo['categoria']}")
    st.write(f"**Fornitore:** {articolo['fornitore']}")
    
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        st.metric(label=f"Quantità Usata ({articolo['unita']})", value=articolo['quantita_usata'])
    with q_col2:
        st.metric(label=f"Quantità Ordinata ({articolo['unita']})", value=articolo['quantita_ordine'])
    
    if articolo['quantita_ordine'] > 0:
        quantita_usata_per_calcolo = max(0, articolo['quantita_usata'])
        percentuale = (quantita_usata_per_calcolo / articolo['quantita_ordine']) * 100
        st.progress(min(percentuale / 100, 1.0))
        st.caption(f"Utilizzo: {percentuale:.1f}% del totale ordinato")

    st.divider()

    # Form per aggiungere/rimuovere quantità
    st.subheader("Gestione Quantità")
    with st.form("modifica_quantita"):
        operazione = st.radio("Operazione:", ["Aggiungi", "Rimuovi"])
        quantita = st.number_input("Quantità:", min_value=1, value=1)
        submit = st.form_submit_button("Conferma Operazione")
        if submit:
            username = st.session_state.get("username", "utente_sconosciuto")
            response = handle_quantity_update(
                article=articolo,
                operation=operazione,
                quantity=quantita,
                username=username
            )
            if response.get("success"):
                st.success(f"Operazione completata: {operazione} {quantita} {articolo['unita']}")
                st.rerun()
            else:
                st.error(response.get("message", "Errore durante l'operazione"))

# --- Colonna Destra: Immagine e Movimenti Recenti ---
with main_col2:
    # Mostra l'immagine dell'articolo
    if articolo.get('url') and articolo['url'].strip():
        st.image(
            articolo['url'],
            caption=f"Immagine di {articolo['descrizione']}",
            use_container_width=True
        )
    else:
        st.info("Nessuna immagine disponibile per questo articolo.")

    st.divider()
    
    # Mostra le transazioni
    st.subheader("Movimenti Recenti")
    is_admin = "user_roles" in st.session_state and "admin" in st.session_state.user_roles
    
    if is_admin:
        st.success(f"Accesso come amministratore: {st.session_state.get('username')}")
        col_mod, col_del = st.columns(2)
        with col_mod:
            if st.button("✏️ Modifica Articolo"):
                st.switch_page("pages/modifica_articolo.py")
        with col_del:
            if st.button("🗑️ Elimina Articolo", type="primary"):
                st.session_state.show_delete_confirm = True
        
        if st.session_state.get("show_delete_confirm"):
            st.warning(f"Sei sicuro di voler eliminare l'articolo '{articolo['descrizione']}'?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Sì, elimina"):
                    result = delete_article(articolo['codice'])
                    if result["success"]:
                        st.success(result["message"])
                        del st.session_state.articolo_selezionato
                        st.session_state.show_delete_confirm = False
                        st.switch_page("app.py")
                    else:
                        st.error(result["message"])
            with col_no:
                if st.button("No, annulla"):
                    st.session_state.show_delete_confirm = False
                    st.rerun()
    
    display_transactions(articolo.get('transazioni', []), articolo['codice'], is_admin=is_admin)

# --- Navigazione ---
st.divider()
if st.button("Torna alla Homepage"):
    if "articolo_selezionato" in st.session_state:
        del st.session_state.articolo_selezionato
    st.switch_page("app.py")