# pages/login.py

import streamlit as st
import streamlit_authenticator as stauth

def login_flow():
    """
    Gestisce l'intero flusso di autenticazione leggendo da st.secrets.
    Restituisce True se l'utente è autenticato, False altrimenti.
    """
    try:
        # Legge la configurazione direttamente dai secrets di Streamlit
        config = st.secrets

        authenticator = stauth.Authenticate(
            config.credentials, # Usa la notazione a punto
            config.cookie.name,
            config.cookie.key,
            config.cookie.expiry_days
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
            user_info = config.credentials.usernames[username]
            st.session_state["user_roles"] = user_info.get('roles', ['viewer'])
            
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