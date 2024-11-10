from fastapi import APIRouter, HTTPException
from llm_utils import parse_document
from llm_utils import llm_chain, retrieval_chain
from models import QueryRequest, QueryAnswerRequest
import os

router = APIRouter()

UPLOAD_FOLDER = "./temp_files/"

@router.post("/query-answer")
async def query_answer(request: QueryAnswerRequest):
    document_path = os.path.join(UPLOAD_FOLDER, request.document_name)
    if not os.path.exists(document_path):
        raise HTTPException(status_code=404, detail=f"Document '{request.document_name}' not found.")
    document_text = parse_document(document_path)
    inputs = {"document": document_text, "query": request.query}
    response = llm_chain.run(inputs)
    return {"query": request.query, "response": response}

@router.post("/query-retrieve")
async def query_retrieve(request: QueryRequest):
    result = retrieval_chain.invoke({"question": request.query})
    source_metadata = [{"document": doc.metadata['source']} for doc in result.get('source_documents', [])]
    return {
        "query": request.query,
        "response": result.get("result", ""),
        "sources": source_metadata
    }
