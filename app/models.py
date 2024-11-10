from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class QueryAnswerRequest(QueryRequest):
    document_name: str
