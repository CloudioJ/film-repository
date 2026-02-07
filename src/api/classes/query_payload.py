from pydantic import BaseModel

class ActorRequest(BaseModel):
    ator: str

class MovieRequest(BaseModel):
    titulo: str

class DirectorRequest(BaseModel):
    diretor: str