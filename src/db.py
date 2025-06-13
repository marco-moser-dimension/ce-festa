"""
Modulo per la gestione del database (file JSON)
"""
import json
import datetime

import os
import datetime

# Ottieni il percorso assoluto della directory principale del progetto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Costruisci il percorso assoluto al file data.json
DATA_FILE = os.path.join(BASE_DIR, 'data_con_fornitore.json')

def read_data(file_path=DATA_FILE):
    """
    Legge il file JSON e restituisce i dati.
    
    Args:
        file_path: Percorso del file JSON
        
    Returns:
        list: Dati letti dal file JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        raise Exception(f"Errore nella lettura del file: {str(e)}")

def write_data(data, file_path=DATA_FILE):
    """
    Scrive i dati nel file JSON.
    
    Args:
        data: Dati da scrivere
        file_path: Percorso del file JSON
        
    Returns:
        bool: True se la scrittura è avvenuta con successo
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        raise Exception(f"Errore nella scrittura del file: {str(e)}")

def get_all_articles(file_path=DATA_FILE, categoria=None, fornitore=None):
    """
    Carica e mappa gli articoli da un file JSON.
    Restituisce una lista di dizionari.
    
    Args:
        file_path: Percorso del file JSON
        categoria: Se specificata, filtra gli articoli per categoria
        fornitore: Se specificato, filtra gli articoli per fornitore
        
    Returns:
        list: Lista di articoli mappati
    """
    try:
        data = read_data(file_path)
        result = []
        
        # Il nuovo formato è un dizionario con categorie come chiavi
        for cat_name, articoli in data.items():
            # Se è specificata una categoria e non è quella corrente, salta
            if categoria and categoria != cat_name and categoria != "Tutte":
                continue
                
            # Mappa i dati nel formato che ci serve per l'app
            for articolo in articoli:
                # Se è specificato un fornitore e non è quello corrente, salta
                if fornitore and fornitore != articolo.get("Fornitore", "") and fornitore != "Tutti":
                    continue
                    
                result.append({
                    "codice": articolo.get("Articolo", "N/D"), 
                    "descrizione": articolo.get("Descrizione_articolo", "Senza descrizione"),
                    "unita": articolo.get("Unita_di_misura", "N/D"),
                    "url": articolo.get("url", ""),  # URL dell'immagine se presente
                    "quantita_usata": int(articolo.get("Quantita_Usata", "0")),  # Quantità utilizzata
                    "quantita_ordine": float(articolo.get("Quantita_in_ordine", "0").replace(",", ".") if isinstance(articolo.get("Quantita_in_ordine"), str) else articolo.get("Quantita_in_ordine", 0)),  # Quantità ordinata
                    "transazioni": articolo.get("transazioni", []),  # Storico transazioni
                    "categoria": cat_name,  # Categoria dell'articolo
                    "fornitore": articolo.get("Fornitore", "")  # Fornitore dell'articolo
                })
        
        return result
    except FileNotFoundError:
        raise Exception(f"Errore: File non trovato al percorso '{file_path}'")
    except json.JSONDecodeError:
        raise Exception(f"Errore: Il file '{file_path}' non è un JSON valido.")

def get_article_by_code(code, file_path=DATA_FILE):
    """
    Trova un articolo per codice.
    
    Args:
        code: Codice dell'articolo
        file_path: Percorso del file JSON
        
    Returns:
        dict: Articolo trovato o None
    """
    articles = get_all_articles(file_path)
    for article in articles:
        if article["codice"] == code:
            return article
    return None

def search_articles(query, file_path=DATA_FILE, categoria=None, fornitore=None):
    """
    Cerca articoli per descrizione o codice.
    
    Args:
        query: Testo da cercare
        file_path: Percorso del file JSON
        categoria: Se specificata, filtra gli articoli per categoria
        fornitore: Se specificato, filtra gli articoli per fornitore
        
    Returns:
        list: Articoli trovati
    """
    if not query:
        return get_all_articles(file_path, categoria, fornitore)
    
    articles = get_all_articles(file_path, categoria, fornitore)
    query = query.lower()
    
    return [
        article for article in articles 
        if query in article["descrizione"].lower() or query in article["codice"].lower()
    ]

def update_article_quantity(article_code, quantity, username, file_path=DATA_FILE):
    """
    Aggiorna la quantità di un articolo e registra la transazione.
    
    Args:
        article_code: Codice dell'articolo
        quantity: Quantità da aggiungere/rimuovere (positiva o negativa)
        username: Username dell'utente che ha effettuato la transazione
        file_path: Percorso del file JSON
        
    Returns:
        dict: Risultato dell'operazione
    """
    try:
        # Leggi il file JSON
        data = read_data(file_path)
        
        # Cerca l'articolo nel file (ora organizzato per categorie)
        article_found = False
        
        for categoria, articoli in data.items():
            for item in articoli:
                if item["Articolo"] == article_code:
                    article_found = True
                    
                    # Converti la quantità usata in numero
                    try:
                        used_quantity = int(item["Quantita_Usata"])
                    except ValueError:
                        used_quantity = 0
                    
                    # Aggiorna la quantità usata
                    used_quantity += int(quantity)
                    item["Quantita_Usata"] = str(used_quantity)
                    
                    # Ottieni l'ora corrente
                    current_time = datetime.datetime.now().strftime("%H:%M:%S")
                    
                    # Aggiungi la transazione all'array transazioni (crealo se non esiste)
                    if "transazioni" not in item:
                        item["transazioni"] = []
                    
                    # Aggiungi la nuova transazione
                    transaction_id = f"{current_time}_{username}_{quantity}"
                    item["transazioni"].append({
                        "id": transaction_id,
                        "time": current_time,
                        "referente": username,
                        "quantità": quantity
                    })
                    
                    break
            
            if article_found:
                break
        
        if not article_found:
            return {"success": False, "message": f"Articolo {article_code} non trovato"}
        
        # Scrivi il file JSON aggiornato
        write_data(data, file_path)
        
        return {
            "success": True, 
            "message": f"Transazione registrata per l'articolo {article_code}",
            "quantità": quantity,
            "time": current_time,
            "referente": username
        }
    
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}

def delete_transaction(article_code, transaction_id, file_path=DATA_FILE):
    """
    Elimina una transazione specifica di un articolo.
    
    Args:
        article_code: Codice dell'articolo
        transaction_id: ID della transazione da eliminare (può essere il campo time)
        file_path: Percorso del file JSON
        
    Returns:
        dict: Risultato dell'operazione
    """
    try:
        # Leggi il file JSON
        data = read_data(file_path)
        
        # Cerca l'articolo nel file (ora organizzato per categorie)
        article_found = False
        transaction_found = False
        transaction_quantity = 0
        
        for categoria, articoli in data.items():
            for item in articoli:
                if item["Articolo"] == article_code:
                    article_found = True
                    
                    # Cerca la transazione
                    if "transazioni" in item:
                        for i, transaction in enumerate(item["transazioni"]):
                            # Controlla sia l'ID che il campo time
                            if (transaction.get("id") == transaction_id or 
                                transaction.get("time") == transaction_id):
                                transaction_found = True
                                try:
                                    transaction_quantity = int(transaction.get("quantità", 0))
                                except ValueError:
                                    transaction_quantity = 0
                                # Rimuovi la transazione
                                item["transazioni"].pop(i)
                                break
                    
                    # Non aggiorniamo la quantità usata, eliminiamo solo la transazione
                    break
            
            if article_found:
                break
        
        if not article_found:
            return {"success": False, "message": f"Articolo {article_code} non trovato"}
        
        if not transaction_found:
            return {"success": False, "message": f"Transazione non trovata"}
        
        # Scrivi il file JSON aggiornato
        write_data(data, file_path)
        
        return {
            "success": True, 
            "message": f"Transazione eliminata per l'articolo {article_code}",
            "quantità": transaction_quantity
        }
    
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}

def delete_all_transactions(article_code, file_path=DATA_FILE):
    """
    Elimina tutte le transazioni di un articolo.
    
    Args:
        article_code: Codice dell'articolo
        file_path: Percorso del file JSON
        
    Returns:
        dict: Risultato dell'operazione
    """
    try:
        # Leggi il file JSON
        data = read_data(file_path)
        
        # Cerca l'articolo nel file (ora organizzato per categorie)
        article_found = False
        
        for categoria, articoli in data.items():
            for item in articoli:
                if item["Articolo"] == article_code:
                    article_found = True
                    
                    # Rimuovi tutte le transazioni
                    item["transazioni"] = []
                    
                    # Non reimpostiamo la quantità usata
                    break
            
            if article_found:
                break
        
        if not article_found:
            return {"success": False, "message": f"Articolo {article_code} non trovato"}
        
        # Scrivi il file JSON aggiornato
        write_data(data, file_path)
        
        return {
            "success": True, 
            "message": f"Tutte le transazioni eliminate per l'articolo {article_code}"
        }
    
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}

def get_all_transactions(file_path=DATA_FILE):
    """
    Ottiene tutte le transazioni da tutti gli articoli.
    
    Args:
        file_path: Percorso del file JSON
        
    Returns:
        list: Lista di tutte le transazioni con informazioni sull'articolo
    """
    try:
        # Leggi il file JSON
        data = read_data(file_path)
        
        all_transactions = []
        
        # Itera su tutte le categorie e articoli
        for categoria, articoli in data.items():
            for item in articoli:
                if "transazioni" in item and item["transazioni"]:
                    article_code = item.get("Articolo", "N/D")
                    article_description = item.get("Descrizione_articolo", "Senza descrizione")
                    article_unit = item.get("Unita_di_misura", "N/D")
                    
                    # Itera su tutte le transazioni dell'articolo
                    for trans in item["transazioni"]:
                        # Crea un dizionario con le informazioni della transazione e dell'articolo
                        transaction = {
                            "article_code": article_code,
                            "article_description": article_description,
                            "article_unit": article_unit,
                            "categoria": categoria,
                            "time": trans.get("time", "N/D"),
                            "referente": trans.get("referente", "N/D"),
                            "quantità": trans.get("quantità", 0)
                        }
                        
                        all_transactions.append(transaction)
        
        # Ordina le transazioni per data/ora (più recenti prima)
        all_transactions.sort(key=lambda x: x["time"], reverse=True)
        
        return all_transactions
    
    except Exception as e:
        print(f"Errore nel recupero delle transazioni: {str(e)}")
        return []

def delete_transaction_by_details(article_code, transaction_time, referente, file_path=DATA_FILE):
    """
    Elimina una transazione specifica di un articolo in base ai dettagli.
    
    Args:
        article_code: Codice dell'articolo
        transaction_time: Orario della transazione
        referente: Utente che ha effettuato la transazione
        file_path: Percorso del file JSON
        
    Returns:
        dict: Risultato dell'operazione
    """
    try:
        # Leggi il file JSON
        data = read_data(file_path)
        
        # Cerca l'articolo nel file (ora organizzato per categorie)
        article_found = False
        transaction_found = False
        
        for categoria, articoli in data.items():
            for item in articoli:
                if item["Articolo"] == article_code:
                    article_found = True
                    
                    # Cerca la transazione
                    if "transazioni" in item:
                        for i, transaction in enumerate(item["transazioni"]):
                            if (transaction.get("time") == transaction_time and 
                                transaction.get("referente") == referente):
                                transaction_found = True
                                # Rimuovi la transazione
                                item["transazioni"].pop(i)
                                break
                    
                    break
            
            if article_found:
                break
        
        if not article_found:
            return {"success": False, "message": f"Articolo {article_code} non trovato"}
        
        if not transaction_found:
            return {"success": False, "message": f"Transazione non trovata"}
        
        # Scrivi il file JSON aggiornato
        write_data(data, file_path)
        
        return {
            "success": True, 
            "message": f"Transazione eliminata per l'articolo {article_code}"
        }
    
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}