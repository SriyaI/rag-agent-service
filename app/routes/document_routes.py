import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from document_utils import parse_document, index_documents

router = APIRouter()
UPLOAD_FOLDER = "./temp_files/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    document_text = parse_document(file_path)
    index_documents(document_text, file.filename)
    return {"message": "File uploaded and indexed successfully", "document_name": file.filename}
