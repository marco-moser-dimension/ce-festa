# pages/transazioni.py (CORRETTO)

import streamlit as st
from src.db import get_all_transactions, delete_transaction_by_details, get_article_by_code

st.set_page_config(page_title="Tutte le Transazioni", page_icon="📊", layout="wide")

if "username" not in st.session_state:
    st.error("Devi effettuare il login per accedere a questa pagina.")
    st.stop()

is_admin = "user_roles" in st.session_state and "admin" in st.session_state.user_roles

st.title("📊 Registro Transazioni")
st.write("Visualizza tutte le transazioni registrate nel sistema.")

transactions = get_all_transactions()

# Filtri
st.subheader("Filtri")
col1, col2, col3 = st.columns(3)

with col1:
    article_desc = ["Tutti"] + sorted(list(set([f"{t['article_code']} - {t['article_description']}" for t in transactions])))
    selected_article_desc = st.selectbox("Filtra per Articolo:", article_desc)

with col2:
    users = ["Tutti"] + sorted(list(set([t["referente"] for t in transactions])))
    selected_user = st.selectbox("Filtra per Utente:", users)

with col3:
    operations = ["Tutte", "Aggiunte", "Rimozioni"]
    selected_operation = st.selectbox("Filtra per Operazione:", operations)

# Applica i filtri
filtered_transactions = transactions
if selected_article_desc != "Tutti":
    selected_code = selected_article_desc.split(" - ")[0]
    filtered_transactions = [t for t in filtered_transactions if t["article_code"] == selected_code]
if selected_user != "Tutti":
    filtered_transactions = [t for t in filtered_transactions if t["referente"] == selected_user]
if selected_operation != "Tutte":
    op_filter = 1 if selected_operation == "Aggiunte" else -1
    filtered_transactions = [t for t in filtered_transactions if int(t["quantità"]) * op_filter > 0]

st.subheader(f"Transazioni Trovate: {len(filtered_transactions)}")

if not filtered_transactions:
    st.info("Nessuna transazione trovata con i filtri selezionati.")
else:
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
    
    if is_admin:
        st.subheader("Azioni Amministratore")
        # MODIFICA: Logica di selezione semplificata
        trans_options = {
            f"#{i+1}: {t['time']} - {t['article_description']} ({t['referente']})": t
            for i, t in enumerate(filtered_transactions)
        }
        selected_trans_text = st.selectbox("Seleziona una transazione da eliminare:", trans_options.keys())
        
        if st.button("Elimina Transazione Selezionata", type="primary"):
            selected_trans_data = trans_options[selected_trans_text]
            response = delete_transaction_by_details(
                article_code=selected_trans_data["article_code"],
                transaction_time=selected_trans_data["time"],
                referente=selected_trans_data["referente"]
            )
            if response.get("success"):
                st.success("Transazione eliminata con successo!")
                st.rerun()
            else:
                st.error(response.get("message"))

st.divider()
if st.button("Torna alla Homepage"):
    st.switch_page("app.py")