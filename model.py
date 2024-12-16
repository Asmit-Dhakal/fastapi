from pydantic import BaseModel


# Request Models
class FolderRequest(BaseModel):
    folder_name: str

class DocumentRequest(BaseModel):
    document_name: str
    folder_id: str

# Response Models
class FolderResponse(BaseModel):
    folder_id: str
    folder_name: str
    archive: bool

class DocumentResponse(BaseModel):
    document_id: str
    document_name: str
    folder_id: str
    archive: bool

# Archive Update Model
class ArchiveStatusUpdate(BaseModel):
    is_archived: bool
