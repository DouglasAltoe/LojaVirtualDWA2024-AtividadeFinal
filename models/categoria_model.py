from dataclasses import dataclass
from typing import Optional

@dataclass
class Categoria:
    id: Optional[int] = None
    descricao: Optional[str] = None
