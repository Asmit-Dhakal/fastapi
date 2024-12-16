from pymongo import MongoClient

def get_database():
    # MongoDB Connection URI
    client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI if needed
    db = client["document_management"]
    folders_collection = db["folders"]
    documents_collection = db["documents"]
    return folders_collection, documents_collection
