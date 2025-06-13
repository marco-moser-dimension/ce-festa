# pages/login.py (VERSIONE CON COPIA PROFONDA TRAMITE JSON)

import streamlit as st
import streamlit_authenticator as stauth
import json # <-- Aggiungi questo import

def login_flow():
    """
    Gestisce l'intero flusso di autenticazione leggendo da st.secrets
    e creando una copia profonda delle credenziali.
    """
    try:
        # ================================================================= #
        # MODIFICA CHIAVE: Creiamo una copia profonda e indipendente        #
        # ================================================================= #
        
        # 1. Converti l'oggetto Secrets in un dizionario standard
        secrets_dict = st.secrets.to_dict()
        
        # 2. Estrai le sezioni che ci servono
        credentials = secrets_dict.get('credentials', {})
        cookie_config = secrets_dict.get('cookie', {})

        # Verifica che le configurazioni essenziali esistano
        if not credentials or not cookie_config:
            st.error("Le sezioni 'credentials' o 'cookie' mancano nel file secrets.toml.")
            return False

        authenticator = stauth.Authenticate(
            credentials,
            cookie_config.get('name'),
            cookie_config.get('key'),
            cookie_config.get('expiry_days')
        )

        authenticator.login()

        if st.session_state["authentication_status"]:
            authenticator.logout(location='sidebar')
            st.sidebar.title(f"Benvenuto, {st.session_state['name']}! 👋")
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("### Menu")
            if st.sidebar.button("📊 Registro Transazioni"):
                st.switch_page("pages/transazioni.py")
            
            # Salva i ruoli dell'utente nella sessione
            username = st.session_state["username"]
            try:
                user_roles = credentials['usernames'][username]['roles']
                st.session_state["user_roles"] = user_roles
            except (AttributeError, KeyError):
                st.session_state["user_roles"] = ["viewer"]
            
            return True
        
        elif st.session_state["authentication_status"] is False:
            st.error('Username/password non corretti')
            return False
        
        elif st.session_state["authentication_status"] is None:
            st.warning('Per favore, inserisci username e password')
            return False

    except Exception as e:
        st.error(f"Errore nel processo di login: {e}")
        st.error("Controlla che il file .streamlit/secrets.toml sia configurato correttamente.")
        return False
    
    return False