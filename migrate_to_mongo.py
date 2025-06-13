# migrate_to_mongo.py
import json
from pymongo import MongoClient

# --- CONFIGURAZIONE ---
# INCOLLA QUI LA TUA STRINGA DI CONNESSIONE COMPLETA
MONGO_CONNECTION_STRING = "mongodb+srv://marcomoser:StFP1K9BdJ27oIqm@cluster0.qbihfmk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

DB_NAME = "ce-festa"
COLLECTION_NAME = "prodotti"
JSON_FILE_PATH = "data_con_fornitore.json" # Assicurati che questo file sia nella stessa cartella
# --------------------

def migrate_data():
    # ... (copia e incolla il resto dello script di migrazione che ti ho dato prima) ...
    print("Connessione a MongoDB...")
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    print("Connessione riuscita.")

    print(f"Lettura del file JSON: {JSON_FILE_PATH}...")
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    articles_to_insert = []
    for category_name, articles in data.items():
        for article in articles:
            article['categoria'] = category_name
            try:
                q_ordine_str = str(article.get("Quantita_in_ordine", "0")).replace(",", ".")
                article["Quantita_in_ordine"] = float(q_ordine_str)
            except (ValueError, TypeError):
                article["Quantita_in_ordine"] = 0.0
            try:
                article["Quantita_Usata"] = int(article.get("Quantita_Usata", "0"))
            except (ValueError, TypeError):
                article["Quantita_Usata"] = 0
            if "transazioni" not in article:
                article["transazioni"] = []
            articles_to_insert.append(article)
    
    print(f"Trasformati {len(articles_to_insert)} articoli pronti per l'inserimento.")

    if articles_to_insert:
        print("Cancellazione dati esistenti nella collezione...")
        collection.delete_many({})
        print("Inserimento nuovi dati...")
        collection.insert_many(articles_to_insert)
        print("Migrazione completata con successo!")
    else:
        print("Nessun articolo da migrare.")

if __name__ == "__main__":
    migrate_data()