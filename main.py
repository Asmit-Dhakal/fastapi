from fastapi import FastAPI, HTTPException
from typing import Optional
from bson import ObjectId

# Import database connection and models
from db_connection import get_database
from model import FolderRequest, DocumentRequest, FolderResponse, DocumentResponse, ArchiveStatusUpdate

app = FastAPI()

# MongoDB collections
folders_collection, documents_collection = get_database()

# Create Folder
@app.post("/folder/", response_model=FolderResponse)
async def create_folder(folder: FolderRequest):
    # Check if folder with the same name already exists
    folder_exists = folders_collection.find_one({"folder_name": folder.folder_name})
    if folder_exists:
        raise HTTPException(status_code=400, detail="Folder already exists")

    # Insert folder data into the database
    folder_data = {
        "folder_name": folder.folder_name.lower(),
        "archive": False
    }
    result = folders_collection.insert_one(folder_data)
    folder_id = str(result.inserted_id)

    # Return folder details
    return FolderResponse(
        folder_id=folder_id,
        folder_name=folder.folder_name,
        archive=False
    )

# Create Document
@app.post("/document/", response_model=DocumentResponse)
async def create_document(document: DocumentRequest):
    # Validate  folder exists
    folder = folders_collection.find_one({"_id": ObjectId(document.folder_id)})
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Insert into the database
    document_data = {
        "document_name": document.document_name.lower(),
        "folder_id": ObjectId(document.folder_id),
        "archive": False
    }
    result = documents_collection.insert_one(document_data)
    document_id = str(result.inserted_id)

    return DocumentResponse(
        document_id=document_id,
        document_name=document.document_name,
        folder_id=document.folder_id,
        archive=False
    )

# Get Folder by Name
@app.get("/folders/{folder_name}", response_model=Optional[FolderResponse])
async def get_folder_by_name(folder_name: str):
    # Find folder by name
    folder = folders_collection.find_one({"folder_name": folder_name})

    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Return folder details
    return FolderResponse(
        folder_id=str(folder["_id"]),
        folder_name=folder["folder_name"],
        archive=folder["archive"]
    )

# Get document by Name
@app.get("/documents/{document_name}", response_model=Optional[DocumentResponse])
async def get_document_by_name(document_name: str):
    # Search for the document by name (case-insensitive)
    document = documents_collection.find_one({"document_name": document_name.lower()})
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Return the document details
    return DocumentResponse(
        document_id=str(document["_id"]),
        document_name=document["document_name"],
        folder_id=str(document["folder_id"]),
        archive=document["archive"]
    )

