from pydantic import BaseModel

class QueryRequest(BaseModel):
    ator: str
    titulo: str
    diretor: str