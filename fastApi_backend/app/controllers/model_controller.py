import httpx
from fastapi import HTTPException
import os
from typing import List, Dict, Optional
from pydantic import BaseModel

class ModelDetails(BaseModel):
    parent_model: str
    format: str
    family: str
    families: List[str]
    parameter_size: str
    quantization_level: str

class ModelInfo(BaseModel):
    name: str
    model: str
    modified_at: str
    size: int
    digest: str
    details: ModelDetails

class ModelController:
    @staticmethod
    async def get_all_models() -> List[ModelInfo]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{os.getenv('OLLAMA_BASE_URL')}/api/tags")
                if response.status_code == 200:
                    print(response.json(), flush=True)
                    return [ModelInfo(**model) for model in response.json()['models']]
                raise HTTPException(status_code=response.status_code, detail="Failed to fetch models")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Generated by Copilot
