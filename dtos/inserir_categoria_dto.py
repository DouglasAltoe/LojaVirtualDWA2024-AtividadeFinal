from pydantic import BaseModel, field_validator
from util.validators import *


class InserirCategoriaDto(BaseModel):
    descricao: str

    @field_validator("descricao")
    def validar_descricao(cls, v):
        msg = is_not_empty(v, "Descrição")
        msg = msg or is_size_between(v, "Descrição", 1, 1024)
        if msg: 
            raise ValueError(msg)
        return v
