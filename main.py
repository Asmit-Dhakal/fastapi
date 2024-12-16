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
        "folder_name": folder.folder_name,
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
    # Validate that the folder exists
    folder = folders_collection.find_one({"_id": ObjectId(document.folder_id)})
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Insert document data into the database
    document_data = {
        "document_name": document.document_name,
        "folder_id": ObjectId(document.folder_id),
        "archive": False
    }
    result = documents_collection.insert_one(document_data)
    document_id = str(result.inserted_id)

    # Return document details
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

# Update Folder Archive Status
@app.patch("/folder/{folder_id}/archive", response_model=FolderResponse)
async def update_folder_archive_status(folder_id: str, status_update: ArchiveStatusUpdate):
    # Update archive status in the database
    result = folders_collection.update_one(
        {"_id": ObjectId(folder_id)},
        {"$set": {"archive": status_update.is_archived}}
    )

    # Check if folder exists
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Return updated folder details
    folder = folders_collection.find_one({"_id": ObjectId(folder_id)})
    return FolderResponse(
        folder_id=str(folder["_id"]),
        folder_name=folder["folder_name"],
        archive=folder["archive"]
    )
