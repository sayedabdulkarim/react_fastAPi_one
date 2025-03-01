from pydantic import BaseModel

class QueryRequest(BaseModel):
    model: str
    prompt: str

class QueryResponse(BaseModel):
    response: str

# Generated by Copilot
