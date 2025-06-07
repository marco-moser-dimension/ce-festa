import json
import os

DATA_FILE = './data.json'

def read_file(file_path=DATA_FILE):
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

def write_file(data, file_path=DATA_FILE):
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

def upload(articolo, alimento, quantità, time, referente):
    """
    Aggiorna il file JSON con una nuova transazione.
    
    Args:
        articolo: Codice dell'articolo
        alimento: Descrizione dell'articolo
        quantità: Quantità da aggiungere/rimuovere
        time: Orario della transazione (formato h:m:s)
        referente: Username dell'utente che ha effettuato la transazione
    
    Returns:
        dict: Risultato dell'operazione
    """
    try:
        # Leggi il file JSON
        data = read_file()
        
        # Cerca l'articolo nel file
        articolo_trovato = False
        for item in data:
            if item["Articolo"] == articolo:
                articolo_trovato = True
                
                # Converti la quantità presa in numero
                try:
                    quantita_presa = int(item["Quantità Presa"])
                except ValueError:
                    quantita_presa = 0
                
                # Aggiorna la quantità presa
                quantita_presa += int(quantità)
                item["Quantità Presa"] = str(quantita_presa)
                
                # Aggiungi la transazione all'array transazioni (crealo se non esiste)
                if "transazioni" not in item:
                    item["transazioni"] = []
                
                # Aggiungi la nuova transazione
                item["transazioni"].append({
                    "time": time,
                    "referente": referente,
                    "quantità": quantità
                })
                
                break
        
        if not articolo_trovato:
            return {"success": False, "message": f"Articolo {articolo} non trovato"}
        
        # Scrivi il file JSON aggiornato
        write_file(data)
        
        return {
            "success": True, 
            "message": f"Transazione registrata per {alimento}",
            "quantità": quantità,
            "time": time,
            "referente": referente
        }
    
    except Exception as e:
        return {"success": False, "message": f"Errore: {str(e)}"}
