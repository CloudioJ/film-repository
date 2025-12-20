from fastapi import APIRouter
from src.api.classes import QueryRequest

router = APIRouter()

@router.get("/busca")
async def busca(req: QueryRequest):
    return { "message": "ok" }