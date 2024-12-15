import os
from fastapi import FastAPI, Request,HTTPException
from typing import Union
from pydantic import BaseModel
import uuid

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient

app = FastAPI()

# Models for Document and Folder

#Request Model
class FolderRequest(BaseModel):
    folder_name: str

class DocumentRequest(BaseModel):
    document_name: str
    folder_id: str

# Response Model
class FolderResponse(BaseModel):
    folder_id: str
    folder_name: str
    archive: bool

class DocumentResponse(BaseModel):
    document_id: str
    document_name: str
    folder_id: str
    archive: bool

class ArchiveStatusUpdate(BaseModel):
    is_archived: bool


#Directory
Local_Storage = "./local_folders"
if not os.path.exists(Local_Storage): os.makedirs((Local_Storage))



""""
# Endpoint for
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/",response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})
    
"""


# Endpoint for hello with name and age
@app.get("/hello/{name}")
async def say_hello(name: str, age: int):
    return {"name": name, "age": age}


folders_db = {}
documents_db = {}
# folder create
@app.post("/folder/")
async def create_Folder(folder: FolderRequest):
    unique_folder_id = str(uuid.uuid4())

    if unique_folder_id  in folders_db:
        raise HTTPException(status_code=404, detail="Folder already there")

    folder_path =os.path.join(Local_Storage,  unique_folder_id)
    try:
        os.makedirs(folder_path)
    except FileExistsError:
        raise HTTPException(status_code=404, detail="Folder already there")

    folders_db[unique_folder_id] = folder.dict()
    return FolderResponse(         # Return FolderResponse
        folder_id=unique_folder_id,
        folder_name=folder.folder_name,
        archive=False
    )


@app.post("/document/")
async def create_Document(document: DocumentRequest):

    unique_document_id = str(uuid.uuid4())

    # Check folder
    if document.folder_id not in folders_db:
        raise HTTPException(status_code=404, detail="Folder not found")

    # Store
    document_data = {
        "document_id": unique_document_id,
        "document_name": document.document_name,
        "folder_id": document.folder_id,
        "archive": False # initial archive
    }

    documents_db[unique_document_id] = document_data

    return DocumentResponse(
        document_id=unique_document_id,
        document_name=document.document_name,
        folder_id=document.folder_id,
        archive=False # initial archive
    )

@app.get("/folders/{name}")
async def get_folder_by_name(folder_name: str):
    # Search
    for folder_id, folder in folders_db.items():
        if folder["folder_name"].lower() == folder_name.lower():
            return{
                "folder_id": folder_id,
                "folder_name": folder["folder_name"],
                "archive": folder["archive"]
            }

    raise HTTPException(status_code=404, detail="Folder not found")


@app.get("/documents/{folder_id}")
async def get_documents_in_folder(folder_id: str):
    # Check  the folder
    if folder_id not in folders_db:
        raise HTTPException(status_code=404, detail="Folder not found")

    # documents for  folder
    documents_in_folder = [
        {"document_id": document_data["document_id"], "name": document_data["document_name"]}
        for document_data in documents_db.values() if document_data["folder_id"] == folder_id
    ]

    return documents_in_folder




@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


