# src/db_connection.py
import streamlit as st
from pymongo import MongoClient

@st.cache_resource
def get_mongo_client():
    connection_string = st.secrets["mongo"]["connection_string"]
    client = MongoClient(connection_string)
    return client

def get_db():
    client = get_mongo_client()
    return client.MagazzinoDB # Puoi cambiare "MagazzinoDB" se vuoi

def get_collection(collection_name: str):
    db = get_db()
    return db[collection_name]