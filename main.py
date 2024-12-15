from fastapi import FastAPI, Request
from typing import Union
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient

# Models for Document and Folder

class Folder(BaseModel):
    folder_id: str
    name: str
    archive: bool

class DocumentData(BaseModel):
    document_id: str
    name: str
    folder_id: str
    archive: bool

class ArchiveStatusUpdate(BaseModel):
    is_archived: bool

app = FastAPI()

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
async def create_Folder(folder: Folder):
    folders_db[folder.folder_id] = folder
    return {"folder": folder}

@app.post("/document/")
async def create_Document(document: DocumentData):
    documents_db[document.ID] = document
    return {"document": document}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


