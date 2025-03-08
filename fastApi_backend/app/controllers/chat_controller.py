from typing import List, Optional
from fastapi import HTTPException
from datetime import datetime
import logging
from ..models.chat_schemas import ChatThread, Message
from ..utils.mongodb import MongoDB
from .model_controller import ModelController

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatController:
    COLLECTION_NAME = "chat_threads"
    
    @staticmethod
    async def get_thread(thread_id: str) -> ChatThread:
        """Get a chat thread by its ID"""
        collection = await MongoDB.get_collection(ChatController.COLLECTION_NAME)
        thread_data = await collection.find_one({"id": thread_id})
        
        if not thread_data:
            raise HTTPException(status_code=404, detail="Chat thread not found")
            
        return ChatThread(**thread_data)
    
    @staticmethod
    async def get_all_threads(user_id: Optional[str] = None, limit: int = 20) -> List[ChatThread]:
        """Get all chat threads for a user, or all threads if no user_id is provided"""
        collection = await MongoDB.get_collection(ChatController.COLLECTION_NAME)
        
        # Filter by user_id if provided
        filter_query = {"user_id": user_id} if user_id else {}
        
        # Get threads sorted by updated_at in descending order
        cursor = collection.find(filter_query).sort("updated_at", -1).limit(limit)
        threads = [ChatThread(**thread) async for thread in cursor]
        
        return threads
    
    @staticmethod
    async def create_thread(message: str, model: str, user_id: Optional[str] = None) -> ChatThread:
        """Create a new chat thread with an initial user message and model response"""
        try:
            # Create user message
            user_message = Message(role="user", content=message)
            
            logger.info(f"Getting model response for message: '{message[:30]}...' using model: {model}")
            # Get response from the model
            response = await ModelController.chat(model, message)
            
            # Create assistant message
            assistant_message = Message(
                role="assistant",
                content=response["response"]
            )
            
            # Create new chat thread
            thread = ChatThread(
                messages=[user_message, assistant_message],
                model=model,
                user_id=user_id,
                title=message[:30] + "..." if len(message) > 30 else message  # Use first part of message as title
            )
            
            # Save to database
            thread_dict = thread.dict()
            logger.info(f"Saving new chat thread to database with ID: {thread.id}")
            
            collection = await MongoDB.get_collection(ChatController.COLLECTION_NAME)
            insert_result = await collection.insert_one(thread_dict)
            
            if not insert_result.acknowledged:
                logger.error("MongoDB insert operation was not acknowledged")
                raise HTTPException(status_code=500, detail="Failed to save chat thread to database")
                
            logger.info(f"Successfully saved chat thread with ID: {thread.id}")
            
            # Verify the data was inserted
            saved_thread = await collection.find_one({"id": thread.id})
            if not saved_thread:
                logger.error(f"Could not verify chat thread {thread.id} was saved")
                raise HTTPException(status_code=500, detail="Failed to verify chat thread was saved")
                
            logger.info(f"Verified chat thread was saved with {len(saved_thread['messages'])} messages")
            
            return thread
        except Exception as e:
            logger.error(f"Error creating chat thread: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    async def add_message_to_thread(
        thread_id: str, 
        message: str, 
        model: str
    ) -> ChatThread:
        """Add a user message and get an AI response in an existing thread"""
        # Get the existing thread
        thread = await ChatController.get_thread(thread_id)
        
        # Create user message
        user_message = Message(role="user", content=message)
        thread.messages.append(user_message)
        
        # Get response from the model
        # Include all previous messages for context (format them appropriately for the model)
        context = "\n".join([f"{msg.role}: {msg.content}" for msg in thread.messages])
        response = await ModelController.chat(model, context)
        
        # Create assistant message
        assistant_message = Message(
            role="assistant",
            content=response["response"]
        )
        thread.messages.append(assistant_message)
        
        # Update timestamp
        thread.updated_at = datetime.utcnow()
        
        # Save to database
        collection = await MongoDB.get_collection(ChatController.COLLECTION_NAME)
        await collection.update_one(
            {"id": thread_id},
            {"$set": thread.dict()}
        )
        
        return thread
    
    @staticmethod
    async def delete_thread(thread_id: str) -> bool:
        """Delete a chat thread"""
        collection = await MongoDB.get_collection(ChatController.COLLECTION_NAME)
        result = await collection.delete_one({"id": thread_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Chat thread not found")
            
        return True
        
# Generated by Copilot
