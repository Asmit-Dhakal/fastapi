from fastapi import FastAPI, HTTPException
from typing import Optional, List
from bson import ObjectId
from db_connection import get_database
from model import FolderRequest, DocumentRequest, FolderResponse, DocumentResponse, ArchiveStatusUpdate

app = FastAPI()

# MongoDB collections
folders_collection, documents_collection = get_database()

# Create Folder
@app.post("/folder/", response_model=FolderResponse)
async def createFolder(folder: FolderRequest):
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

# Get All Folders
@app.get("/folders/", response_model=List[FolderResponse])
async def get_all_folders():
    folders = folders_collection.find()
    return [
        FolderResponse(
            folder_id=str(folder["_id"]),
            folder_name=folder["folder_name"],
            archive=folder["archive"]
        ) for folder in folders
    ]

# Get Folder by Name
@app.get("/folders/{folder_name}", response_model=Optional[FolderResponse])
async def getFolderByName(folder_name: str):
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


# Delete Folder and associated Documents
@app.delete("/folder/{folder_id}", response_model=FolderResponse)
async def delete_folder(folder_id: str):

    folder = folders_collection.find_one({"_id": str(folder_id)})
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Delete all documents associated with the folder
    documents_collection.delete_many({"folder_id": str(folder_id)})

    # Delete the folder
    result = folders_collection.delete_one({"_id": str(folder_id)})

    # Check
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Return the deleted folder details
    return FolderResponse(
        folder_id=str(folder["_id"]),
        folder_name=folder["folder_name"],
        archive=folder["archive"]
    )

# Update Folder Archive Status
@app.patch("/folder/{folder_id}/archive", response_model=FolderResponse)
async def update_folder_archive_status(folder_id: str, status_update: ArchiveStatusUpdate):
    # Convert 1 to True and 0 to False
    archive_status = True if status_update.is_archived == 1 else False

    # Update archive status of the folder
    result = folders_collection.update_one(
        {"_id": str(folder_id)},
        {"$set": {"archive": archive_status}}
    )

    # Check if folder exists
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Also update archive status for all documents in the folder
    documents_collection.update_many(
        {"folder_id": str(folder_id)},  # Find all documents in this folder
        {"$set": {"archive": archive_status}}  # Set their archive status
    )

    # Return updated folder details
    folder = folders_collection.find_one({"_id": str(folder_id)})
    return FolderResponse(
        folder_id=str(folder["_id"]),
        folder_name=folder["folder_name"],
        archive=folder["archive"]
    )



# Create Document
@app.post("/document/", response_model=DocumentResponse)
async def createDocument(document: DocumentRequest):
    # Validate folder exists
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


# Get Document by Name
@app.get("/documents/{document_name}", response_model=Optional[DocumentResponse])
async def getDocumentByName(document_name: str):
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



# Update Document Archive Status
@app.patch("/document/{document_id}/archive", response_model=DocumentResponse)
async def update_document_archive_status(document_id: str, status_update: ArchiveStatusUpdate):
    # Convert 1 to True and 0 to False
    archive_status = True if status_update.is_archived == 1 else False

    # Update the archive status in the database
    result = documents_collection.update_one(
        {"_id": ObjectId(document_id)},
        {"$set": {"archive": archive_status}}
    )

    # Check if the document exists
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")


    # Return updated document details
    document = documents_collection.find_one({"_id": ObjectId(document_id)})
    return DocumentResponse(
        document_id=str(document["_id"]),
        document_name=document["document_name"],
        folder_id=str(document["folder_id"]),
        archive=document["archive"]
    )
