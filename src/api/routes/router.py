from fastapi import APIRouter
from src.api.classes import ActorRequest, MovieRequest, DirectorRequest
from src.sparql import SparQL

router = APIRouter()
sparql = SparQL("ontologies/movies-ontology-master/ontology.rdf")

@router.get("/actor_search")
async def actor_search(req: ActorRequest):
    print(f"Dados recebidos: {req}")
    result = sparql.query_by_actor(req.ator)
    return { "result": result }

@router.get("/movie_search")
async def movie_search(req: MovieRequest):
    print(f"Dados recebidos: {req}")
    result = sparql.query_by_movie(req.titulo)
    return { "result": result }

@router.get("/director_search")
async def actor_search(req: DirectorRequest):
    print(f"Dados recebidos: {req}")
    result = sparql.query_by_director(req.diretor)
    return { "result": result }