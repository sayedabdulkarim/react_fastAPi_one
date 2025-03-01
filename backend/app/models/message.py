from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Message(BaseModel):
    content: str
    timestamp: Optional[datetime] = None
    role: str = "user"

class MessageResponse(BaseModel):
    content: str
    timestamp: datetime = datetime.now()
    role: str = "assistant"

# Generated by Copilot
