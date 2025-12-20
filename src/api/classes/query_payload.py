from pydantic import BaseModel

class QueryRequest(BaseModel):
    ator: str
    titulo: str
    ano: str