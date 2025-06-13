# pages/login.py (VERSIONE FINALE BASATA SUGLI ESEMPI UFFICIALI)

import streamlit as st
import streamlit_authenticator as stauth

def login_flow():
    """
    Gestisce l'intero flusso di autenticazione.
    """
    # 1. Carica la configurazione dai secrets.
    # Usiamo .to_dict() per creare una copia standard e prevenire errori.
    try:
        credentials = st.secrets.credentials.to_dict()
        cookie_config = st.secrets.cookie.to_dict()
    except Exception as e:
        st.error(f"Errore nella lettura di secrets.toml: {e}")
        st.error("Assicurati che le sezioni [credentials] e [cookie] siano presenti e corrette.")
        return False

    # 2. Inizializza l'authenticator.
    # Questo oggetto verrà ricreato ad ogni esecuzione, ma leggerà lo stato
    # dal cookie e da st.session_state.
    authenticator = stauth.Authenticate(
        credentials,
        cookie_config['name'],
        cookie_config['key'],
        cookie_config['expiry_days']
    )

    # 3. Esegui il widget di login.
    # Questa funzione gestisce sia la visualizzazione del form sia la lettura del cookie.
    authenticator.login()

    # 4. Controlla lo stato di autenticazione che la libreria ha impostato.
    if st.session_state.get("authentication_status"):
        # L'utente è loggato.
        with st.sidebar:
            st.title(f"Benvenuto, {st.session_state['name']}! 👋")
            authenticator.logout('Logout', 'main') # Bottone di logout
            
            st.markdown("---")
            st.markdown("### Menu")
            if st.button("📊 Registro Transazioni"):
                st.switch_page("pages/transazioni.py")
        
        # Imposta i ruoli dell'utente per il resto dell'app
        username = st.session_state["username"]
        try:
            st.session_state["user_roles"] = credentials['usernames'][username]['roles']
        except KeyError:
            st.session_state["user_roles"] = ["viewer"]
        
        return True
    
    elif st.session_state.get("authentication_status") is False:
        # Tentativo di login fallito.
        st.error('Username/password non corretti')
        return False
    
    elif st.session_state.get("authentication_status") is None:
        # Stato iniziale, nessun tentativo di login ancora effettuato.
        st.warning('Per favore, inserisci username e password')
        return False
    
    return False