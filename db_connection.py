from pymongo import MongoClient

def get_database():
    # MongoDB Connection URI
    client = MongoClient("mongodb://localhost:27017/")
    db = client["Folder_document"]
    folders_collection = db["folders"]
    documents_collection = db["documents"]
    return folders_collection, documents_collection
