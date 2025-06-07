# pages/login.py

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def login_flow():
    """
    Gestisce l'intero flusso di autenticazione.
    Restituisce True se l'utente è autenticato, False altrimenti.
    """
    try:
        with open('./credentials.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)

        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days']
        )

        authenticator.login()

        if st.session_state["authentication_status"]:
            authenticator.logout(location='sidebar')
            st.sidebar.title(f"Benvenuto, {st.session_state['name']}! 👋")
            return True
        
        elif st.session_state["authentication_status"] is False:
            st.error('Username/password non corretti')
            return False
        
        elif st.session_state["authentication_status"] is None:
            st.warning('Per favore, inserisci username e password')
            return False

    except Exception as e:
        st.error(f"Errore nel processo di login: {e}")
        return False
    
    return False