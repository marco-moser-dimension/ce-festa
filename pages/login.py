# pages/login.py (VERSIONE SEMPLICE E DIRETTA)

import streamlit as st
import streamlit_authenticator as stauth

def login_flow():
    """
    Gestisce l'intero flusso di autenticazione.
    """
    try:
        # 1. Converti i secrets in un dizionario standard. Questo è tutto.
        credentials = st.secrets.credentials.to_dict()
        cookie_config = st.secrets.cookie.to_dict()

        # 2. Inizializza l'authenticator con i dizionari
        authenticator = stauth.Authenticate(
            credentials,
            cookie_config['name'],
            cookie_config['key'],
            cookie_config['expiry_days']
        )

        # 3. Esegui il widget di login
        authenticator.login()

        # 4. Controlla lo stato
        if st.session_state["authentication_status"]:
            with st.sidebar:
                st.title(f"Benvenuto, {st.session_state['name']}! 👋")
                authenticator.logout('Logout', 'main')
                st.markdown("---")
                st.markdown("### Menu")
                if st.button("📊 Registro Transazioni"):
                    st.switch_page("pages/transazioni.py")
            
            # Salva i ruoli dell'utente nella sessione
            username = st.session_state["username"]
            try:
                user_roles = credentials['usernames'][username]['roles']
                st.session_state["user_roles"] = user_roles
            except KeyError:
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