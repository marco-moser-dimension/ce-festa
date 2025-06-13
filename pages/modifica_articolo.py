# pages/modifica_articolo.py

import streamlit as st
from src.db import update_article, get_all_articles, get_article_by_code

st.set_page_config(page_title="Modifica Articolo", page_icon="✏️", layout="wide")

if "user_roles" not in st.session_state or "admin" not in st.session_state["user_roles"]:
    st.error("Non hai i permessi per accedere a questa pagina.")
    st.stop()

# Leggi il codice dall'URL
try:
    codice_articolo = st.query_params["codice"]
except KeyError:
    st.error("Nessun articolo specificato per la modifica.")
    st.stop()

# Carica l'articolo dal DB
articolo = get_article_by_code(codice_articolo)
if not articolo:
    st.error(f"Articolo con codice '{codice_articolo}' non trovato.")
    st.stop()

try:
    tutti_gli_articoli = get_all_articles()
    categorie = sorted(list(set(art['categoria'] for art in tutti_gli_articoli)))
    fornitori = sorted(list(set(art['fornitore'] for art in tutti_gli_articoli if art.get('fornitore'))))
except Exception as e:
    st.error(f"Errore nel caricamento dati: {str(e)}")
    categorie, fornitori = [], []

st.title(f"Modifica Articolo: {articolo['descrizione']}")

with st.form("modifica_articolo_form"):
    codice = st.text_input("Codice Articolo", value=articolo['codice'], disabled=True)
    descrizione = st.text_input("Descrizione", value=articolo['descrizione'])
    unita = st.text_input("Unità di Misura", value=articolo['unita'])
    quantita_ordine = st.number_input("Quantità Ordinata", value=float(articolo['quantita_ordine']), min_value=0.0)
    url_immagine = st.text_input("URL Immagine", value=articolo.get('url', ''))
    
    cat_index = categorie.index(articolo['categoria']) if articolo.get('categoria') in categorie else 0
    categoria_selezionata = st.selectbox("Categoria", options=categorie, index=cat_index)
    
    forn_index = fornitori.index(articolo['fornitore']) if articolo.get('fornitore') in fornitori else 0
    fornitore_selezionato = st.selectbox("Fornitore", options=fornitori, index=forn_index)
    
    submit = st.form_submit_button("Salva Modifiche")
    
    if submit:
        updated_data = {
            "Articolo": codice, "Descrizione_articolo": descrizione, "Unita_di_misura": unita,
            "Quantita_in_ordine": float(quantita_ordine), "Quantita_Usata": int(articolo['quantita_usata']),
            "Fornitore": fornitore_selezionato, "categoria": categoria_selezionata, "url": url_immagine,
            "transazioni": articolo.get("transazioni", [])
        }
        result = update_article(codice, updated_data)
        if result["success"]:
            st.success(result["message"])
            # Aggiorna i query params per tornare alla pagina di dettaglio aggiornata
            st.query_params["codice"] = codice
            st.switch_page("pages/dettaglio_articolo.py")
        else:
            st.error(result["message"])

st.page_link("pages/dettaglio_articolo.py", label="Annulla e torna al dettaglio", icon="↩️", query_params={"codice": articolo['codice']})