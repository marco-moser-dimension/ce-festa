"""
Modulo di utilità per l'applicazione
"""
import streamlit as st
import datetime
from src.db import get_article_by_code, update_article_quantity, delete_transaction, delete_all_transactions

def display_article_gallery(articles, on_article_click=None):
    """
    Mostra una galleria di card data una lista di articoli.
    
    Args:
        articles: Lista di articoli da visualizzare
        on_article_click: Funzione da chiamare quando si clicca su un articolo
    """
    st.divider()

    if not articles:
        st.warning("Nessun articolo trovato per la tua ricerca.")
        return

    # Utilizziamo un container a larghezza piena per la galleria
    with st.container():
        # Determiniamo il numero di colonne in base al numero di articoli
        num_cols = 3  # Utilizziamo 3 colonne per un buon bilanciamento
        
        # Creiamo una griglia di colonne con larghezza massima
        cols = st.columns(num_cols, gap="small")
        
        # Iteriamo sulla lista di articoli e creiamo una card per ognuno
        for i, articolo in enumerate(articles):
            with cols[i % num_cols]:
                with st.container(border=True):
                    # Se è presente un URL dell'immagine, la mostriamo
                    if articolo.get('url') and articolo['url'].strip():
                        # Utilizziamo st.image con dimensioni ridotte
                        st.image(
                            articolo['url'],
                            width=150,  # Larghezza ridotta
                            output_format="JPEG"  # Formato più leggero
                        )
                    
                    # Riduciamo le dimensioni del testo per adattarsi meglio
                    st.markdown(f"### {articolo['descrizione']}")
                    st.caption(f"Codice: {articolo['codice']}")
                    
                    # Mostriamo la categoria e il fornitore
                    if 'categoria' in articolo:
                        st.caption(f"Categoria: {articolo['categoria']}")
                    
                    if 'fornitore' in articolo:
                        st.caption(f"Fornitore: {articolo['fornitore']}")
                    
                    # Mostriamo la quantità usata e ordinata
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            label=f"Usata ({articolo['unita']})", 
                            value=articolo['quantita_usata']
                        )
                    with col2:
                        st.metric(
                            label=f"Ordinata ({articolo['unita']})", 
                            value=articolo['quantita_ordine']
                        )
                    
                    # Il bottone per navigare alla pagina di dettaglio
                    if st.button("Visualizza", key=f"btn_{articolo['codice']}"):
                        if on_article_click:
                            on_article_click(articolo)
                        else:
                            st.session_state.articolo_selezionato = articolo
                            st.switch_page("pages/dettaglio_articolo.py")

def display_article_details(article):
    """
    Mostra i dettagli di un articolo.
    
    Args:
        article: Articolo da visualizzare
    """
    st.title(f"Dettaglio Articolo: {article['descrizione']}")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Informazioni Articolo")
        st.write(f"**Codice:** {article['codice']}")
        st.write(f"**Unità di misura:** {article['unita']}")
        
        # Mostriamo la categoria e il fornitore se presenti
        if 'categoria' in article:
            st.write(f"**Categoria:** {article['categoria']}")
        
        if 'fornitore' in article:
            st.write(f"**Fornitore:** {article['fornitore']}")
        
        # Visualizzazione delle quantità con indicatori metrici
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.metric(
                label=f"Quantità Usata ({article['unita']})", 
                value=article['quantita_usata']
            )
        with col_q2:
            st.metric(
                label=f"Quantità Ordinata ({article['unita']})", 
                value=article['quantita_ordine']
            )
        
        # Calcolo e visualizzazione della percentuale di utilizzo
        if article['quantita_ordine'] > 0:
            percentuale = (article['quantita_usata'] / article['quantita_ordine']) * 100
            st.progress(min(percentuale / 100, 1.0))
            st.caption(f"Utilizzo: {percentuale:.1f}% del totale ordinato")

def handle_quantity_update(article, operation, quantity, username):
    """
    Gestisce l'aggiornamento della quantità di un articolo.
    
    Args:
        article: Articolo da aggiornare
        operation: Operazione da eseguire (Aggiungi o Rimuovi)
        quantity: Quantità da aggiungere/rimuovere
        username: Username dell'utente che ha effettuato la transazione
        
    Returns:
        dict: Risultato dell'operazione
    """
    # Determina il segno della quantità in base all'operazione
    effective_quantity = quantity if operation == "Aggiungi" else -quantity
    
    # Chiama la funzione per aggiornare la quantità
    response = update_article_quantity(
        article_code=article['codice'],
        quantity=effective_quantity,
        username=username
    )
    
    # Se l'operazione è andata a buon fine, aggiorna l'articolo nella sessione
    if response.get("success", False):
        # Aggiorna la quantità usata nell'articolo
        article["quantita_usata"] += effective_quantity
        
        # Aggiungi la transazione all'articolo nella sessione
        if "transazioni" not in article:
            article["transazioni"] = []
        
        # Ottieni l'ora corrente
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        
        article["transazioni"].append({
            "time": current_time,
            "referente": username,
            "quantità": effective_quantity
        })
    
    return response

def display_transactions(transactions, article_code, is_admin=False):
    """
    Mostra una tabella con le transazioni.
    
    Args:
        transactions: Lista di transazioni da visualizzare
        article_code: Codice dell'articolo
        is_admin: Se True, mostra i controlli di amministrazione
    """
    # Verifica se c'è un messaggio di feedback da mostrare
    if "deleted_transaction" in st.session_state:
        st.success(f"✅ Transazione eliminata: {st.session_state.deleted_transaction}")
        
    if "all_transactions_deleted" in st.session_state:
        st.success("✅ Tutte le transazioni sono state eliminate!")
    if not transactions:
        st.info("Nessun movimento registrato per questo articolo")
        return
    
    # Crea una tabella con le transazioni
    transactions_data = []
    for trans in transactions:
        # Determina se è un'aggiunta o una rimozione
        try:
            quantita = int(trans.get('quantità', 0))
            operation = "Aggiunta" if quantita > 0 else "Rimozione"
            quantity_abs = abs(quantita)
        except ValueError:
            operation = "N/D"
            quantity_abs = 0
        
        transactions_data.append({
            "Ora": trans.get('time', 'N/D'),
            "Operazione": operation,
            "Quantità": quantity_abs,
            "Utente": trans.get('referente', 'N/D')
        })
    
    # Mostra la tabella delle transazioni
    st.dataframe(
        transactions_data,
        use_container_width=True,
        hide_index=True
    )
    
    # Se l'utente è admin, mostra i controlli per eliminare le transazioni
    if is_admin:
        
        st.divider()
        st.subheader("Amministrazione Transazioni")
        
        # Elimina una singola transazione
        with st.expander("Elimina una transazione"):
            # Crea un selettore per le transazioni
            transaction_options = []
            for trans in transactions:
                time = trans.get('time', 'N/D')
                referente = trans.get('referente', 'N/D')
                
                try:
                    quantita = int(trans.get('quantità', 0))
                    operation = "Aggiunta" if quantita > 0 else "Rimozione"
                    quantity_abs = abs(quantita)
                except ValueError:
                    operation = "N/D"
                    quantity_abs = 0
                    quantita = 0
                
                option_text = f"{time} - {operation} {quantity_abs} ({referente})"
                # Usa il campo time come ID della transazione
                transaction_id = time
                
                transaction_options.append((option_text, transaction_id))
            
            if transaction_options:
                selected_option = st.selectbox(
                    "Seleziona la transazione da eliminare:",
                    options=[text for text, _ in transaction_options],
                    key="transaction_select"
                )
                
                # Trova l'ID della transazione selezionata
                selected_index = [text for text, _ in transaction_options].index(selected_option)
                selected_transaction_id = transaction_options[selected_index][1]
                
                if st.button("Elimina Transazione", key="delete_transaction"):
                    # Salva la transazione selezionata per il feedback
                    st.session_state.deleted_transaction = selected_option
                    
                    # Esegui l'eliminazione
                    response = delete_transaction(article_code, selected_transaction_id)
                    
                    if response.get("success", False):
                        # Ottieni l'articolo aggiornato dal database
                        updated_article = get_article_by_code(article_code)
                        if updated_article and "articolo_selezionato" in st.session_state:
                            # Aggiorna l'articolo nella sessione
                            st.session_state.articolo_selezionato = updated_article
                        
                        # Mostra il feedback
                        st.success(f"✅ Transazione eliminata: {selected_option}")
                        
                        # Ricarica la pagina
                        st.rerun()
                    else:
                        st.error(response.get("message", "Errore durante l'eliminazione della transazione"))
            else:
                st.info("Nessuna transazione disponibile")
        
        # Elimina tutte le transazioni
        with st.expander("Elimina tutte le transazioni"):
            st.warning("Questa operazione eliminerà tutte le transazioni per questo articolo e resetterà la quantità usata a 0.")
            if st.button("Elimina Tutte le Transazioni", key="delete_all_transactions"):
                # Salva l'informazione che tutte le transazioni sono state eliminate
                st.session_state.all_transactions_deleted = True
                
                # Salva il numero di transazioni per il feedback
                num_transactions = len(transactions)
                
                # Esegui l'eliminazione
                response = delete_all_transactions(article_code)
                
                if response.get("success", False):
                    # Ottieni l'articolo aggiornato dal database
                    updated_article = get_article_by_code(article_code)
                    if updated_article and "articolo_selezionato" in st.session_state:
                        # Aggiorna l'articolo nella sessione
                        st.session_state.articolo_selezionato = updated_article
                    
                    # Mostra il feedback
                    st.success("✅ Tutte le transazioni sono state eliminate!")
                    st.info(f"Sono state eliminate {num_transactions} transazioni.")
                    
                    # Ricarica la pagina
                    st.rerun()
                else:
                    st.error(response.get("message", "Errore durante l'eliminazione delle transazioni"))