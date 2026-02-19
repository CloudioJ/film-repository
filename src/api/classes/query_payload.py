from pydantic import BaseModel

class ActorRequest(BaseModel):
    ator: str
    direct: bool

class MovieRequest(BaseModel):
    titulo: str
    direct: bool

class DirectorRequest(BaseModel):
    diretor: str
    direct: bool