from fastapi import APIRouter
from src.api.classes import QueryRequest
from src.sparql import SparQL

router = APIRouter()
sparql = SparQL("ontologies/movies-ontology-master/ontology.rdf")

@router.get("/busca")
async def busca(req: QueryRequest):
    print(f"Dados recebidos: {req}")
    result = sparql.query(req.ator, req.titulo, req.ano)
    return { "result": result }