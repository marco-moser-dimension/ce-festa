# app.py (Versione Semplificata, Pulita e Funzionale)

import streamlit as st
import json
from pages.login import login_flow 

# Configurazione della pagina per massimizzare lo spazio
st.set_page_config(
    page_title="Homepage Magazzino", 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="collapsed"  # Collassa la sidebar per massimizzare lo spazio
)

# --- 1. FUNZIONI DI SUPPORTO (Logica Incapsulata) ---

def load_articles(file_path: str) -> list:
    """
    Carica e mappa gli articoli da un file JSON.
    Restituisce una lista di dizionari.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Mappa i dati nel formato che ci serve per l'app
        return [
            {
                "codice": articolo.get("Articolo", "N/D"), 
                "descrizione": articolo.get("Descrizione articolo", "Senza descrizione"),
                "unita": articolo.get("Unità di misura", "N/D"),
                "url": articolo.get("url", ""),  # URL dell'immagine se presente
                "quantita": int(articolo.get("Quantità Presa", "0")),  # Quantità presa
                "transazioni": articolo.get("transazioni", [])  # Storico transazioni
            } 
            for articolo in data
        ]
    except FileNotFoundError:
        st.error(f"Errore: File non trovato al percorso '{file_path}'")
        return []
    except json.JSONDecodeError:
        st.error(f"Errore: Il file '{file_path}' non è un JSON valido.")
        return []

def display_header_and_search_bar():
    """
    Mostra il titolo della pagina e la barra di ricerca.
    La magia della ricerca live avviene qui.
    """
    st.title("Dashboard Magazzino 📦")
    st.write("Cerca un articolo o selezionalo dalla lista per vederne i dettagli.")

    # Questo è il modo più semplice e robusto per una ricerca live:
    # 1. 'key' collega il valore del widget a st.session_state.search_query.
    # 2. Ogni volta che l'utente digita, lo stato cambia e Streamlit riesegue lo script.
    st.text_input(
        "Cerca un articolo per descrizione...",
        key="search_query", # La chiave è tutto ciò che serve
        placeholder="Es. pasta, formaggio, acqua..."
    )

def display_article_gallery(articles: list):
    """
    Mostra una galleria di card data una lista di articoli.
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
                    
                    # Mostriamo la quantità presa
                    st.metric(
                        label=f"Quantità ({articolo['unita']})", 
                        value=articolo['quantita']
                    )
                    
                    # Il bottone per navigare alla pagina di dettaglio
                    if st.button("Visualizza", key=f"btn_{articolo['codice']}"):
                        st.session_state.articolo_selezionato = articolo
                        st.switch_page("pages/dettaglio_articolo.py")

# --- 2. FLUSSO PRINCIPALE DELL'APPLICAZIONE ---

# Esegui il login. Se non va a buon fine, ferma tutto.
if not login_flow():
    st.stop()

# Inizializza la variabile di stato per la ricerca, se non esiste
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# Carica i dati una sola volta
tutti_gli_articoli = load_articles('./data.json')

# Mostra l'intestazione e la barra di ricerca
display_header_and_search_bar()

# Filtra gli articoli in base alla query di ricerca (che è in st.session_state)
query = st.session_state.search_query.lower()
if query:
    articoli_filtrati = [
        articolo for articolo in tutti_gli_articoli 
        if query in articolo["descrizione"].lower() or query in articolo["codice"].lower()
    ]
else:
    articoli_filtrati = tutti_gli_articoli[:40]  # Limitiamo a 40 articoli per default per migliorare le performance

# Mostra la galleria con gli articoli filtrati
display_article_gallery(articoli_filtrati)