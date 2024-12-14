from pydantic import BaseModel
from typing import List
class Document(BaseModel):
   ID: object
   name: str
   folder_id:str
   archive: bool

class Folder(BaseModel):
    folder_id: str
    name: object
    archive: bool




