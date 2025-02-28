from pydantic import BaseModel

class Message(BaseModel):
    content: str
    
class MessageResponse(BaseModel):
    message: str
    status: str = "success"

# Generated by Copilot
