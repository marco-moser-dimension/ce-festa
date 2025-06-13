import json

# --- CONFIGURAZIONE ---
# Modifica queste tre variabili secondo le tue necessità

# 1. Il nome del fornitore che vuoi aggiungere a tutti gli articoli in questo file.
nome_fornitore = "Segata" 

# 2. Il nome del file JSON di input (quello che mi hai fornito).
file_input = "data_copy.json"

# 3. Il nome del file JSON di output che verrà creato.
file_output = "data_con_fornitore.json"
# --------------------


try:
    # 1. Carica il file JSON in una variabile Python (un dizionario)
    with open(file_input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Itera attraverso ogni categoria e ogni articolo per aggiungere il nuovo campo
    #    data.values() prende tutte le liste di articoli (es. la lista di "Verdura", ecc.)
    for lista_articoli in data.values():
        # Itera su ogni singolo articolo (che è un dizionario) nella lista
        for articolo in lista_articoli:
            # Aggiunge la nuova coppia chiave-valore all'articolo
            articolo['Fornitore'] = nome_fornitore

    # 3. Salva il dizionario modificato in un nuovo file JSON
    #    - indent=4 formatta il file in modo che sia leggibile (come l'originale)
    #    - ensure_ascii=False preserva i caratteri speciali e accentati (fondamentale per l'italiano)
    with open(file_output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Operazione completata con successo!")
    print(f"Il fornitore '{nome_fornitore}' è stato aggiunto a tutti gli articoli.")
    print(f"Il risultato è stato salvato nel file: '{file_output}'")

except FileNotFoundError:
    print(f"Errore: Il file '{file_input}' non è stato trovato. Assicurati che sia nella stessa cartella dello script.")
except Exception as e:
    print(f"Si è verificato un errore inaspettato: {e}")