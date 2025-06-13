# pages/transazioni.py (VERSIONE CORRETTA E COMPLETA)

import streamlit as st
from src.db import get_all_transactions, delete_transaction_by_details, get_article_by_code

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Tutte le Transazioni", page_icon="📊", layout="wide")

# --- CONTROLLI DI ACCESSO ---
if "username" not in st.session_state:
    st.error("Devi effettuare il login per accedere a questa pagina.")
    if st.button("Vai alla Homepage"):
        st.switch_page("app.py")
    st.stop()

is_admin = "user_roles" in st.session_state and "admin" in st.session_state.user_roles

# --- CONTENUTO DELLA PAGINA ---
st.title("📊 Registro Transazioni")
st.write("Visualizza e filtra tutte le transazioni registrate nel sistema.")

try:
    transactions = get_all_transactions()
except Exception as e:
    st.error(f"Impossibile caricare le transazioni dal database: {e}")
    transactions = []

# --- FILTRI ---
st.subheader("Filtri")
col1, col2, col3 = st.columns(3)

with col1:
    # Crea una lista di descrizioni uniche per il filtro
    article_descriptions = ["Tutti"] + sorted(list(set(f"{t['article_code']} - {t['article_description']}" for t in transactions)))
    selected_article_desc = st.selectbox("Filtra per Articolo:", article_descriptions)

with col2:
    users = ["Tutti"] + sorted(list(set(t["referente"] for t in transactions)))
    selected_user = st.selectbox("Filtra per Utente:", users)

with col3:
    operations = ["Tutte", "Aggiunte", "Rimozioni"]
    selected_operation = st.selectbox("Filtra per Operazione:", operations)

# --- APPLICA FILTRI ---
filtered_transactions = transactions
if selected_article_desc != "Tutti":
    selected_code = selected_article_desc.split(" - ")[0]
    filtered_transactions = [t for t in filtered_transactions if t["article_code"] == selected_code]
if selected_user != "Tutti":
    filtered_transactions = [t for t in filtered_transactions if t["referente"] == selected_user]
if selected_operation != "Tutte":
    op_filter = 1 if selected_operation == "Aggiunte" else -1
    filtered_transactions = [t for t in filtered_transactions if int(t["quantità"]) * op_filter > 0]

# --- VISUALIZZAZIONE TABELLA ---
st.subheader(f"Transazioni Trovate: {len(filtered_transactions)}")

if not filtered_transactions:
    st.info("Nessuna transazione trovata con i filtri selezionati.")
else:
    # Prepara i dati per il DataFrame di Streamlit
    df_data = [
        {
            "Ora": t["time"],
            "Articolo": f"{t['article_code']} - {t['article_description']}",
            "Operazione": "Aggiunta" if int(t['quantità']) > 0 else "Rimozione",
            "Quantità": f"{abs(int(t['quantità']))} {t['article_unit']}",
            "Utente": t["referente"]
        } for t in filtered_transactions
    ]
    st.dataframe(df_data, use_container_width=True, hide_index=True)

    # --- SEZIONE AZIONI (SE CI SONO TRANSAZIONI) ---
    st.divider()
    st.subheader("Azioni sulla Transazione Selezionata")

    # Crea le opzioni per il selettore
    transaction_options = {
        f"#{i+1}: {t['time']} - {t['article_description']} ({t['referente']})": t
        for i, t in enumerate(filtered_transactions)
    }
    
    selected_transaction_text = st.selectbox(
        "Seleziona una transazione per visualizzare le azioni:",
        options=transaction_options.keys()
    )
    
    # Ottieni i dati della transazione selezionata
    selected_transaction = transaction_options[selected_transaction_text]

    # MODIFICA: Reintroduciamo i dettagli della transazione e i pulsanti di azione
    st.write("**Dettagli Transazione Selezionata:**")
    st.json({
        "Articolo": f"{selected_transaction['article_code']} - {selected_transaction['article_description']}",
        "Data/Ora": selected_transaction["time"],
        "Quantità": f"{abs(int(selected_transaction['quantità']))} {selected_transaction['article_unit']}",
        "Operazione": "Aggiunta" if int(selected_transaction["quantità"]) > 0 else "Rimozione",
        "Utente": selected_transaction["referente"]
    })

    # Layout per i pulsanti di azione
    action_cols = st.columns(3)

    with action_cols[0]:
        # Pulsante per andare alla pagina di dettaglio dell'articolo
        if st.button("Vai all'Articolo", key="go_to_article"):
            article = get_article_by_code(selected_transaction["article_code"])
            if article:
                st.session_state.articolo_selezionato = article
                st.switch_page("pages/dettaglio_articolo.py")
            else:
                st.error(f"Articolo {selected_transaction['article_code']} non trovato.")

    # Mostra il pulsante di eliminazione solo agli admin
    if is_admin:
        with action_cols[1]:
            if st.button("Elimina Transazione", key="delete_transaction", type="primary"):
                response = delete_transaction_by_details(
                    article_code=selected_transaction["article_code"],
                    transaction_time=selected_transaction["time"],
                    referente=selected_transaction["referente"]
                )
                if response.get("success"):
                    st.success("Transazione eliminata con successo dallo storico!")
                    st.rerun()
                else:
                    st.error(response.get("message"))

# --- NAVIGAZIONE ---
st.divider()
if st.button("Torna alla Homepage"):
    st.switch_page("app.py")