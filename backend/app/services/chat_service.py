from datetime import datetime
from typing import List, Dict
from bson import ObjectId
from app.database.mongodb import MongoDB

class ChatService:
    def __init__(self):
        self._db = MongoDB.get_db()
        self._chats = self._db.chats
        self._messages = self._db.messages

    async def create_chat(self, title: str) -> str:
        """Create a new chat thread"""
        result = await self._chats.insert_one({
            "title": title,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        return str(result.inserted_id)

    async def get_chats(self) -> List[Dict]:
        """Get all chat threads"""
        cursor = self._chats.find().sort("updated_at", -1)
        return [{**chat, "_id": str(chat["_id"])} for chat in await cursor.to_list(length=100)]

    async def add_message(self, chat_id: str, role: str, content: str) -> Dict:
        """Add a message to a chat thread"""
        message = {
            "chat_id": ObjectId(chat_id),
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }
        await self._messages.insert_one(message)
        await self._chats.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"updated_at": datetime.utcnow()}}
        )
        return {**message, "_id": str(message["_id"]), "chat_id": chat_id}

    async def get_chat_messages(self, chat_id: str) -> List[Dict]:
        """Get all messages in a chat thread"""
        cursor = self._messages.find({"chat_id": ObjectId(chat_id)}).sort("timestamp", 1)
        return [{**msg, "_id": str(msg["_id"]), "chat_id": str(msg["chat_id"])} 
                for msg in await cursor.to_list(length=1000)]

# Generated by Copilot
