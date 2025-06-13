# pages/dettaglio_articolo.py (CORRETTO)

import streamlit as st
from utils import display_article_details, handle_quantity_update, display_transactions
# MODIFICA: Importiamo get_article_by_code per ricaricare i dati
from src.db import delete_article, get_article_by_code

st.set_page_config(page_title="Dettaglio Articolo", page_icon="📦", layout="wide")

if "articolo_selezionato" not in st.session_state:
    st.error("Nessun articolo selezionato. Torna alla homepage.")
    if st.button("Torna alla Homepage"):
        st.switch_page("app.py")
    st.stop()

if "username" not in st.session_state:
    st.warning("Sessione utente non trovata. Alcune funzionalità potrebbero essere limitate.")
    st.session_state.username = "utente_sconosciuto"

# MODIFICA: Ricarichiamo l'articolo dal DB per avere sempre i dati più freschi
articolo = get_article_by_code(st.session_state.articolo_selezionato['codice'])
if not articolo:
    st.error("Articolo non trovato nel database. Potrebbe essere stato eliminato.")
    st.stop()
st.session_state.articolo_selezionato = articolo # Aggiorna la sessione

display_article_details(articolo)

col1, col2 = st.columns([2, 1])

with col1:
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

with col2:
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

if st.button("Torna alla Homepage"):
    del st.session_state.articolo_selezionato
    st.switch_page("app.py")