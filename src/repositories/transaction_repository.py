# src/repositories/transaction_repository.py
from pymongo.collection import Collection
import datetime

class TransactionRepository:
    # ... (copia e incolla tutto il codice della classe TransactionRepository che ti ho dato prima) ...
    def __init__(self, collection: Collection):
        self.collection = collection

    def update_article_quantity(self, article_code, quantity, username):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        transaction_id = f"{current_time}_{username}_{quantity}"
        
        transaction_doc = {
            "id": transaction_id,
            "time": current_time,
            "referente": username,
            "quantità": quantity
        }

        result = self.collection.update_one(
            {"Articolo": article_code},
            {
                "$inc": {"Quantita_Usata": quantity},
                "$push": {"transazioni": transaction_doc}
            }
        )

        if result.matched_count == 0:
            return {"success": False, "message": f"Articolo {article_code} non trovato"}
        
        return {"success": True, "message": "Transazione registrata con successo"}

    def delete_transaction_by_details(self, article_code, transaction_time, referente):
        article = self.collection.find_one(
            {"Articolo": article_code, "transazioni": {"$elemMatch": {"time": transaction_time, "referente": referente}}},
            {"transazioni.$": 1}
        )

        if not article or not article.get("transazioni"):
            return {"success": False, "message": "Transazione non trovata"}

        transaction_to_delete = article["transazioni"][0]
        quantity_to_revert = -int(transaction_to_delete.get("quantità", 0))

        result = self.collection.update_one(
            {"Articolo": article_code},
            {
                "$pull": {"transazioni": {"time": transaction_time, "referente": referente}},
                "$inc": {"Quantita_Usata": quantity_to_revert}
            }
        )

        if result.modified_count == 0:
            return {"success": False, "message": "Errore durante l'eliminazione della transazione"}
        
        return {"success": True, "message": "Transazione eliminata e quantità stornata"}

    def get_all_transactions(self):
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
        return list(self.collection.aggregate(pipeline))