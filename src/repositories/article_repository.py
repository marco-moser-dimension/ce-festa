# src/repositories/article_repository.py
from pymongo.collection import Collection
import re

class ArticleRepository:
    # ... (copia e incolla tutto il codice della classe ArticleRepository che ti ho dato prima) ...
    def __init__(self, collection: Collection):
        self.collection = collection

    def _map_to_app_format(self, mongo_doc):
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

    def get_all_articles(self, categoria=None, fornitore=None):
        query = {}
        if categoria and categoria != "Tutte":
            query["categoria"] = categoria
        if fornitore and fornitore != "Tutti":
            query["Fornitore"] = fornitore
        
        articles_cursor = self.collection.find(query)
        return [self._map_to_app_format(doc) for doc in articles_cursor]

    def get_article_by_code(self, code):
        mongo_doc = self.collection.find_one({"Articolo": code})
        return self._map_to_app_format(mongo_doc)

    def search_articles(self, search_query, categoria=None, fornitore=None):
        query = {}
        if categoria and categoria != "Tutte":
            query["categoria"] = categoria
        if fornitore and fornitore != "Tutti":
            query["Fornitore"] = fornitore

        if search_query:
            regex = re.compile(search_query, re.IGNORECASE)
            query["$or"] = [
                {"Descrizione_articolo": {"$regex": regex}},
                {"Articolo": {"$regex": regex}}
            ]
        
        articles_cursor = self.collection.find(query)
        return [self._map_to_app_format(doc) for doc in articles_cursor]

    def add_new_article(self, article_data):
        article_code = article_data.get("Articolo")
        if self.collection.find_one({"Articolo": article_code}):
            return {"success": False, "message": f"Articolo con codice {article_code} già esistente"}
        
        result = self.collection.insert_one(article_data)
        return {"success": result.acknowledged, "message": "Articolo aggiunto con successo"}

    def update_article(self, article_code, updated_data):
        result = self.collection.replace_one({"Articolo": article_code}, updated_data)
        if result.matched_count == 0:
            return {"success": False, "message": "Articolo non trovato"}
        return {"success": True, "message": "Articolo aggiornato con successo"}

    def delete_article(self, article_code):
        result = self.collection.delete_one({"Articolo": article_code})
        if result.deleted_count == 0:
            return {"success": False, "message": "Articolo non trovato"}
        return {"success": True, "message": "Articolo eliminato con successo"}