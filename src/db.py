# src/db.py

"""
Modulo per la gestione del database (MongoDB Atlas)
"""
import streamlit as st
from pymongo import MongoClient
import datetime
import re

# --- GESTIONE CONNESSIONE ---
# Questa funzione interna si occupa di connettersi a MongoDB
# e viene messa in cache da Streamlit per efficienza.
@st.cache_resource
def _get_mongo_client():
    """Stabilisce la connessione a MongoDB usando i secrets."""
    connection_string = st.secrets["mongo"]["connection_string"]
    client = MongoClient(connection_string)
    return client

def _get_collection(collection_name: str = "prodotti"):
    """Restituisce un oggetto collezione specifico."""
    client = _get_mongo_client()
    db = client["ce-festa"]  # Usa il nome corretto del database
    return db[collection_name]

# --- FUNZIONE HELPER INTERNA ---
# Per mappare il formato di Mongo a quello che l'app si aspetta
def _map_mongo_doc_to_app_format(mongo_doc):
    """Mappa un documento Mongo nel formato atteso dall'app."""
    if not mongo_doc:
        return None
    return {
        "codice": mongo_doc.get("Articolo", "N/D"),
        "descrizione": mongo_doc.get("Descrizione_articolo", "Senza descrizione"),
        "unita": mongo_doc.get("Unita_di_misura", "N/D"),
        "url": mongo_doc.get("url", ""),
        "quantita_usata": mongo_doc.get("Quantita_Usata", 0),
        "quantita_ordine": mongo_doc.get("Quantita_in_ordine", 0.0),
        "transazioni": mongo_doc.get("transazioni", []),
        "categoria": mongo_doc.get("categoria", "N/D"),
        "fornitore": mongo_doc.get("Fornitore", "N/D")
    }

# --- FUNZIONI PUBBLICHE (interfaccia identica al vecchio db.py) ---

def get_all_articles(categoria=None, fornitore=None):
    """Carica articoli da MongoDB, con filtri opzionali."""
    try:
        collection = _get_collection()
        query = {}
        if categoria and categoria != "Tutte":
            query["categoria"] = categoria
        if fornitore and fornitore != "Tutti":
            query["Fornitore"] = fornitore
        
        articles_cursor = collection.find(query)
        return [_map_mongo_doc_to_app_format(doc) for doc in articles_cursor]
    except Exception as e:
        st.error(f"Errore nel recupero articoli: {e}")
        return []

def get_article_by_code(code):
    """Trova un articolo per codice in MongoDB."""
    try:
        collection = _get_collection()
        mongo_doc = collection.find_one({"Articolo": code})
        return _map_mongo_doc_to_app_format(mongo_doc)
    except Exception as e:
        st.error(f"Errore nel recupero articolo {code}: {e}")
        return None

def search_articles(query, categoria=None, fornitore=None):
    """Cerca articoli per descrizione o codice in MongoDB."""
    try:
        collection = _get_collection()
        db_query = {}
        if categoria and categoria != "Tutte":
            db_query["categoria"] = categoria
        if fornitore and fornitore != "Tutti":
            db_query["Fornitore"] = fornitore

        if query:
            # Regex per ricerca case-insensitive
            regex = re.compile(query, re.IGNORECASE)
            db_query["$or"] = [
                {"Descrizione_articolo": {"$regex": regex}},
                {"Articolo": {"$regex": regex}}
            ]
        
        articles_cursor = collection.find(db_query)
        return [_map_mongo_doc_to_app_format(doc) for doc in articles_cursor]
    except Exception as e:
        st.error(f"Errore nella ricerca articoli: {e}")
        return []

def update_article_quantity(article_code, quantity, username):
    """Aggiorna la quantità di un articolo e registra la transazione in modo atomico."""
    try:
        collection = _get_collection()
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        transaction_id = f"{current_time}_{username}_{quantity}"
        
        transaction_doc = {
            "id": transaction_id,
            "time": current_time,
            "referente": username,
            "quantità": int(quantity)
        }

        result = collection.update_one(
            {"Articolo": article_code},
            {
                "$inc": {"Quantita_Usata": int(quantity)},
                "$push": {"transazioni": transaction_doc}
            }
        )

        if result.matched_count == 0:
            return {"success": False, "message": f"Articolo {article_code} non trovato"}
        
        return {"success": True, "message": "Transazione registrata con successo"}
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}

# ================================================================= #
# MODIFICA CHIAVE: La funzione ora elimina solo la transazione      #
# dallo storico, senza alterare la Quantita_Usata.                  #
# ================================================================= #
def delete_transaction_by_details(article_code, transaction_time, referente):
    """
    Elimina una transazione dallo storico senza modificare la Quantita_Usata.
    """
    try:
        collection = _get_collection()
        
        # Eseguiamo solo l'operazione di $pull per rimuovere la transazione dall'array
        result = collection.update_one(
            {"Articolo": article_code},
            {
                "$pull": {
                    "transazioni": {
                        "time": transaction_time,
                        "referente": referente
                    }
                }
            }
        )

        if result.matched_count == 0:
            return {"success": False, "message": f"Articolo {article_code} non trovato"}
        
        if result.modified_count == 0:
            return {"success": False, "message": "Transazione non trovata o già eliminata"}
        
        return {"success": True, "message": "Transazione eliminata dallo storico"}
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}

def get_all_transactions():
    """Ottiene tutte le transazioni da MongoDB usando una pipeline di aggregazione."""
    try:
        collection = _get_collection()
        pipeline = [
            {"$unwind": "$transazioni"},
            {"$sort": {"transazioni.time": -1}},
            {
                "$project": {
                    "_id": 0,
                    "article_code": "$Articolo",
                    "article_description": "$Descrizione_articolo",
                    "article_unit": "$Unita_di_misura",
                    "categoria": "$categoria",
                    "time": "$transazioni.time",
                    "referente": "$transazioni.referente",
                    "quantità": "$transazioni.quantità"
                }
            }
        ]
        return list(collection.aggregate(pipeline))
    except Exception as e:
        st.error(f"Errore nel recupero transazioni: {e}")
        return []

def add_new_article(article_data, categoria):
    """Aggiunge un nuovo articolo a MongoDB."""
    try:
        collection = _get_collection()
        article_code = article_data.get("Articolo")
        if not article_code:
            return {"success": False, "message": "Codice articolo mancante"}
        
        if collection.find_one({"Articolo": article_code}):
            return {"success": False, "message": f"Articolo con codice {article_code} già esistente"}
        
        # Aggiunge la categoria al dizionario prima di inserirlo
        article_data['categoria'] = categoria
        collection.insert_one(article_data)
        return {"success": True, "message": f"Articolo {article_code} aggiunto con successo"}
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}

def update_article(article_code, updated_data):
    """Aggiorna i dati di un articolo esistente in MongoDB."""
    try:
        collection = _get_collection()
        # Assicuriamoci di non sovrascrivere le transazioni se non sono nei dati aggiornati
        existing_article = collection.find_one({"Articolo": article_code}, {"transazioni": 1})
        if existing_article and "transazioni" in existing_article and "transazioni" not in updated_data:
            updated_data["transazioni"] = existing_article["transazioni"]

        result = collection.replace_one({"Articolo": article_code}, updated_data)
        if result.matched_count == 0:
            return {"success": False, "message": f"Articolo {article_code} non trovato"}
        
        return {"success": True, "message": f"Articolo {article_code} aggiornato con successo"}
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}

def delete_article(article_code):
    """Elimina un articolo da MongoDB."""
    try:
        collection = _get_collection()
        result = collection.delete_one({"Articolo": article_code})
        if result.deleted_count == 0:
            return {"success": False, "message": f"Articolo {article_code} non trovato"}
        
        return {"success": True, "message": f"Articolo {article_code} eliminato con successo"}
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}