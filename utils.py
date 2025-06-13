# utils.py (CORRETTO)

import streamlit as st
import datetime
# MODIFICA: Importiamo solo le funzioni che esistono nel nuovo db.py
from src.db import get_article_by_code, update_article_quantity, delete_transaction_by_details

def display_article_gallery(articles, on_article_click=None):
    """Mostra una galleria di card data una lista di articoli."""
    st.divider()
    if not articles:
        st.warning("Nessun articolo trovato per la tua ricerca.")
        return

    with st.container():
        num_cols = 3
        cols = st.columns(num_cols, gap="small")
        for i, articolo in enumerate(articles):
            with cols[i % num_cols]:
                with st.container(border=True):
                    if articolo.get('url') and articolo['url'].strip():
                        st.image(articolo['url'], width=150, output_format="JPEG")
                    
                    st.markdown(f"### {articolo['descrizione']}")
                    st.caption(f"Codice: {articolo['codice']}")
                    if 'categoria' in articolo:
                        st.caption(f"Categoria: {articolo['categoria']}")
                    if 'fornitore' in articolo:
                        st.caption(f"Fornitore: {articolo['fornitore']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label=f"Usata ({articolo['unita']})", value=articolo['quantita_usata'])
                    with col2:
                        st.metric(label=f"Ordinata ({articolo['unita']})", value=articolo['quantita_ordine'])
                    
                    if st.button("Visualizza", key=f"btn_{articolo['codice']}"):
                        if on_article_click:
                            on_article_click(articolo)
                        else:
                            st.session_state.articolo_selezionato = articolo
                            st.switch_page("pages/dettaglio_articolo.py")

def display_article_details(article):
    """Mostra i dettagli di un articolo."""
    st.title(f"Dettaglio Articolo: {article['descrizione']}")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Informazioni Articolo")
        st.write(f"**Codice:** {article['codice']}")
        st.write(f"**Unità di misura:** {article['unita']}")
        if 'categoria' in article:
            st.write(f"**Categoria:** {article['categoria']}")
        if 'fornitore' in article:
            st.write(f"**Fornitore:** {article['fornitore']}")
        
        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.metric(label=f"Quantità Usata ({article['unita']})", value=article['quantita_usata'])
        with col_q2:
            st.metric(label=f"Quantità Ordinata ({article['unita']})", value=article['quantita_ordine'])
        # in utils.py, dentro display_article_details
        if article['quantita_ordine'] > 0:
            # Usa max(0, ...) per assicurarti che la quantità usata non sia mai negativa nel calcolo
            quantita_usata_per_calcolo = max(0, article['quantita_usata'])
            percentuale = (quantita_usata_per_calcolo / article['quantita_ordine']) * 100
            st.progress(min(percentuale / 100, 1.0))
            st.caption(f"Utilizzo: {percentuale:.1f}% del totale ordinato")        
        

def handle_quantity_update(article, operation, quantity, username):
    """Gestisce l'aggiornamento della quantità di un articolo."""
    effective_quantity = quantity if operation == "Aggiungi" else -quantity
    response = update_article_quantity(
        article_code=article['codice'],
        quantity=effective_quantity,
        username=username
    )
    # MODIFICA: Non aggiorniamo più la sessione manualmente.
    # La pagina si ricaricherà e leggerà i dati freschi dal DB.
    return response

def display_transactions(transactions, article_code, is_admin=False):
    """Mostra una tabella con le transazioni."""
    if not transactions:
        st.info("Nessun movimento registrato per questo articolo")
        return
    
    transactions_data = []
    for trans in transactions:
        try:
            quantita = int(trans.get('quantità', 0))
            operation = "Aggiunta" if quantita > 0 else "Rimozione"
            quantity_abs = abs(quantita)
        except ValueError:
            operation = "N/D"; quantity_abs = 0
        
        transactions_data.append({
            "Ora": trans.get('time', 'N/D'),
            "Operazione": operation,
            "Quantità": quantity_abs,
            "Utente": trans.get('referente', 'N/D')
        })
    
    st.dataframe(transactions_data, use_container_width=True, hide_index=True)
    
    if is_admin:
        st.divider()
        st.subheader("Amministrazione Transazioni")
        with st.expander("Elimina una transazione"):
            # MODIFICA: Semplificata la logica di eliminazione
            transaction_options = {
                f"{t.get('time', 'N/D')} - {'Aggiunta' if int(t.get('quantità', 0)) > 0 else 'Rimozione'} {abs(int(t.get('quantità', 0)))} ({t.get('referente', 'N/D')})": t
                for t in transactions
            }
            
            if transaction_options:
                selected_option_text = st.selectbox(
                    "Seleziona la transazione da eliminare:",
                    options=transaction_options.keys()
                )
                
                if st.button("Elimina Transazione Selezionata", type="primary"):
                    selected_trans = transaction_options[selected_option_text]
                    response = delete_transaction_by_details(
                        article_code,
                        selected_trans.get('time'),
                        selected_trans.get('referente')
                    )
                    
                    if response.get("success"):
                        st.success("Transazione eliminata con successo!")
                        # Aggiorna l'articolo nella sessione per riflettere il cambiamento
                        updated_article = get_article_by_code(article_code)
                        if updated_article:
                            st.session_state.articolo_selezionato = updated_article
                        st.rerun()
                    else:
                        st.error(response.get("message", "Errore sconosciuto"))
            else:
                st.info("Nessuna transazione da eliminare.")