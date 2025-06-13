import streamlit as st
from utils import display_article_details, handle_quantity_update, display_transactions

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
display_article_details(articolo)

# Layout a due colonne
col1, col2 = st.columns([2, 1])

with col1:
    # Form per aggiungere/rimuovere quantità
    st.subheader("Gestione Quantità")
    with st.form("modifica_quantita"):
        operazione = st.radio("Operazione:", ["Aggiungi", "Rimuovi"])
        quantita = st.number_input("Quantità:", min_value=1, value=1)
        
        submit = st.form_submit_button("Conferma Operazione")
        if submit:
            # Ottieni lo username dell'utente corrente dalla sessione
            username = st.session_state.get("username", "utente_sconosciuto")
            
            # Gestisci l'aggiornamento della quantità
            response = handle_quantity_update(
                article=st.session_state.articolo_selezionato,
                operation=operazione,
                quantity=quantita,
                username=username
            )
            
            # Mostra il messaggio di successo o errore
            if response.get("success", False):
                st.success(f"Operazione completata: {operazione} {quantita} {articolo['unita']}")
                st.rerun()  # Ricarica la pagina per mostrare i dati aggiornati
            else:
                st.error(response.get("message", "Errore durante l'operazione"))

with col2:
    # Mostra le transazioni
    st.subheader("Movimenti Recenti")
    
    # Verifica se l'utente è admin
    is_admin = False
    if "username" in st.session_state:
        username = st.session_state.username
        # Verifica se l'utente ha il ruolo di admin
        if "user_roles" in st.session_state and "admin" in st.session_state.user_roles:
            is_admin = True
            st.success(f"Accesso come amministratore: {username}")
            
            # Pulsanti per modificare o eliminare l'articolo (solo per admin)
            col_mod, col_del = st.columns(2)
            with col_mod:
                if st.button("✏️ Modifica Articolo"):
                    st.switch_page("pages/modifica_articolo.py")
            
            with col_del:
                # Pulsante per eliminare l'articolo
                if st.button("🗑️ Elimina Articolo"):
                    st.session_state.show_delete_confirm = True
            
            # Mostra il dialogo di conferma per l'eliminazione
            if st.session_state.get("show_delete_confirm", False):
                st.warning(f"Sei sicuro di voler eliminare l'articolo '{articolo['descrizione']}'?")
                col_yes, col_no = st.columns(2)
                
                with col_yes:
                    if st.button("Sì, elimina"):
                        from src.db import delete_article
                        result = delete_article(articolo['codice'])
                        
                        if result["success"]:
                            st.success(result["message"])
                            # Rimuovi l'articolo selezionato dalla sessione
                            if "articolo_selezionato" in st.session_state:
                                del st.session_state.articolo_selezionato
                            # Torna direttamente alla dashboard
                            st.switch_page("app.py")
                        else:
                            st.error(result["message"])
                
                with col_no:
                    if st.button("No, annulla"):
                        st.session_state.show_delete_confirm = False
                        st.rerun()
    
    display_transactions(
        articolo.get('transazioni', []), 
        articolo['codice'], 
        is_admin=is_admin
    )

# Pulsante per tornare alla homepage
if st.button("Torna alla Homepage"):
    # Rimuovi l'articolo selezionato dalla sessione
    del st.session_state.articolo_selezionato
    st.switch_page("app.py")