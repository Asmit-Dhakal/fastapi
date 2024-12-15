import os
from fastapi import FastAPI, Request,HTTPException
from typing import Union
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient

app = FastAPI()

# Models for Document and Folder

#Request Model
class FolderRequest(BaseModel):
    folder_id: str
    name: str
    archive: bool

class DocumentRequest(BaseModel):
    document_id: str
    name: str
    folder_id: str
    archive: bool

# Response
class FolderResponse(BaseModel):
    folder_id: str
    name: str
    archive: bool

class DocumentResponse(BaseModel):
    document_id: str
    name: str
    folder_id: str
    archive: bool

class ArchiveStatusUpdate(BaseModel):
    is_archived: bool


#Directory
Local_Storage = "./local_folders"
if not os.path.exists(Local_Storage): os.makedirs((Local_Storage))


# Endpoint for
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
@app.get("/",response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})

# Endpoint for hello with name and age
@app.get("/hello/{name}")
async def say_hello(name: str, age: int):
    return {"name": name, "age": age}


folders_db = {}
documents_db = {}
# folder create
@app.post("/folder/")
async def create_Folder(folder: FolderRequest):
    if folder.folder_id  in folders_db:
        raise HTTPException(status_code=404, detail="Folder already there")

    folder_path =os.path.join(Local_Storage, folder.folder_id)
    try:
        os.makedirs(folder_path)
    except FileExistsError:
        raise HTTPException(status_code=404, detail="Folder already there")

    folders_db[folder.folder_id] = folder.dict()
    return folder


@app.post("/document/")
async def create_Document(document: DocumentResponse):
   if document.document_id in documents_db:
       raise HTTPException(status_code=404, detail="Document already there")
   elif document.document_id not in folders_db:
       raise HTTPException(status_code=404, detail="Document not found")
   elif document.folder_id not in folders_db:
       raise HTTPException(status_code=404, detail="Folder not found")
   else:
       documents_db[document.document_id] = document.dict()
       return document


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


