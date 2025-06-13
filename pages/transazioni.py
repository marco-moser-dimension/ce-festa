import streamlit as st
import datetime
from src.db import get_all_transactions, delete_transaction_by_details, get_article_by_code

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Tutte le Transazioni", page_icon="📊", layout="wide")

# Verifica se l'utente è autenticato
if "username" not in st.session_state:
    st.error("Devi effettuare il login per accedere a questa pagina.")
    if st.button("Vai alla Homepage"):
        st.switch_page("app.py")
    st.stop()

# Verifica se l'utente è admin
is_admin = False
if "user_roles" in st.session_state and "admin" in st.session_state.user_roles:
    is_admin = True

# --- Contenuto della pagina ---
st.title("📊 Registro Transazioni")
st.write("Visualizza tutte le transazioni registrate nel sistema.")

# Ottieni tutte le transazioni
transactions = get_all_transactions()

# Filtri
st.subheader("Filtri")
col1, col2, col3 = st.columns(3)

with col1:
    # Filtro per articolo
    article_codes = ["Tutti"] + list(set([t["article_code"] for t in transactions]))
    selected_article = st.selectbox("Filtra per Articolo:", article_codes)

with col2:
    # Filtro per utente
    users = ["Tutti"] + list(set([t["referente"] for t in transactions]))
    selected_user = st.selectbox("Filtra per Utente:", users)

with col3:
    # Filtro per tipo di operazione
    operations = ["Tutte", "Aggiunte", "Rimozioni"]
    selected_operation = st.selectbox("Filtra per Operazione:", operations)

# Applica i filtri
filtered_transactions = transactions.copy()

if selected_article != "Tutti":
    filtered_transactions = [t for t in filtered_transactions if t["article_code"] == selected_article]

if selected_user != "Tutti":
    filtered_transactions = [t for t in filtered_transactions if t["referente"] == selected_user]

if selected_operation != "Tutte":
    if selected_operation == "Aggiunte":
        filtered_transactions = [t for t in filtered_transactions if int(t["quantità"]) > 0]
    else:  # Rimozioni
        filtered_transactions = [t for t in filtered_transactions if int(t["quantità"]) < 0]

# Mostra la tabella delle transazioni
st.subheader(f"Transazioni ({len(filtered_transactions)})")

if not filtered_transactions:
    st.info("Nessuna transazione trovata con i filtri selezionati.")
else:
    # Prepara i dati per la tabella
    table_data = []
    for i, trans in enumerate(filtered_transactions):
        # Determina se è un'aggiunta o una rimozione
        try:
            quantita = int(trans["quantità"])
            operation = "Aggiunta" if quantita > 0 else "Rimozione"
            quantity_abs = abs(quantita)
        except ValueError:
            operation = "N/D"
            quantity_abs = 0
        
        # Crea una riga per la tabella
        row = {
            "ID": i + 1,
            "Data/Ora": trans["time"],
            "Articolo": f"{trans['article_code']} - {trans['article_description']}",
            "Operazione": operation,
            "Quantità": f"{quantity_abs} {trans['article_unit']}",
            "Utente": trans["referente"]
        }
        table_data.append(row)
    
    # Mostra la tabella
    with st.container(height=400):
        st.dataframe(
            table_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.NumberColumn(
                    "ID",
                    help="ID della transazione",
                    width="small"
                ),
                "Data/Ora": st.column_config.TextColumn(
                    "Data/Ora",
                    help="Data e ora della transazione",
                    width="medium"
                ),
                "Articolo": st.column_config.TextColumn(
                    "Articolo",
                    help="Codice e descrizione dell'articolo",
                    width="large"
                ),
                "Operazione": st.column_config.TextColumn(
                    "Operazione",
                    help="Tipo di operazione",
                    width="medium"
                ),
                "Quantità": st.column_config.TextColumn(
                    "Quantità",
                    help="Quantità movimentata",
                    width="medium"
                ),
                "Utente": st.column_config.TextColumn(
                    "Utente",
                    help="Utente che ha effettuato l'operazione",
                    width="medium"
                )
            }
        )
    
    # Azioni sulle transazioni
    st.subheader("Azioni")
    
    # Seleziona una transazione
    selected_index = st.selectbox(
        "Seleziona una transazione:",
        options=list(range(1, len(filtered_transactions) + 1)),
        format_func=lambda x: f"#{x} - {filtered_transactions[x-1]['time']} - {filtered_transactions[x-1]['article_description']}"
    )
    
    # Ottieni la transazione selezionata
    selected_transaction = filtered_transactions[selected_index - 1]
    
    # Mostra i dettagli della transazione selezionata
    st.write("**Dettagli Transazione:**")
    st.json({
        "Articolo": f"{selected_transaction['article_code']} - {selected_transaction['article_description']}",
        "Data/Ora": selected_transaction["time"],
        "Quantità": f"{abs(int(selected_transaction['quantità']))} {selected_transaction['article_unit']}",
        "Operazione": "Aggiunta" if int(selected_transaction["quantità"]) > 0 else "Rimozione",
        "Utente": selected_transaction["referente"]
    })
    
    # Pulsanti per le azioni
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Vai all'articolo
        if st.button("Vai all'Articolo", key="go_to_article"):
            # Ottieni l'articolo completo
            article = get_article_by_code(selected_transaction["article_code"])
            if article:
                st.session_state.articolo_selezionato = article
                st.switch_page("pages/dettaglio_articolo.py")
            else:
                st.error(f"Articolo {selected_transaction['article_code']} non trovato.")
    
    # Solo gli admin possono eliminare le transazioni
    if is_admin:
        with col2:
            # Elimina la transazione
            if st.button("Elimina Transazione", key="delete_transaction"):
                response = delete_transaction_by_details(
                    article_code=selected_transaction["article_code"],
                    transaction_time=selected_transaction["time"],
                    referente=selected_transaction["referente"]
                )
                
                if response.get("success", False):
                    st.success(f"✅ Transazione eliminata con successo!")
                    st.rerun()
                else:
                    st.error(response.get("message", "Errore durante l'eliminazione della transazione"))
    
    # Pulsante per tornare alla homepage
    st.divider()
    if st.button("Torna alla Homepage"):
        st.switch_page("app.py")