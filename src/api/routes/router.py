from fastapi import APIRouter
from src.api.classes import ActorRequest, MovieRequest, DirectorRequest
from src.sparql import SparQL

router = APIRouter()
sparql = SparQL("ontologies/movies-ontology-master/ontology.rdf")

@router.post("/actor_search")
async def actor_search(req: ActorRequest):
    print(f"Dados recebidos: {req}")
    result = sparql.query_by_actor(req.ator, req.direct)
    result = sparql.query_by_actor(req.ator, req.direct)
    return { "result": result }

@router.post("/movie_search")
async def movie_search(req: MovieRequest):
    print(f"Dados recebidos: {req}")
    result = sparql.query_by_movie(req.titulo, req.direct)
    return { "result": result }

@router.post("/director_search")
async def director_search(req: DirectorRequest):
    print(f"Dados recebidos: {req}")
    result = sparql.query_by_director(req.diretor, req.direct)
    return { "result": result }