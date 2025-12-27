from pydantic import BaseModel
from typing import Optional

class VarianteBase(BaseModel):
    id_Producto: int
    color: str
    talla: str
    stock: int

class VarianteCreate(VarianteBase):
    idVariante: int
    
class VarianteUpdate(BaseModel):
    id_Producto: Optional[int] = None
    color: Optional[str] = None
    talla: Optional[str] = None
    stock: Optional[int] = None
    
class Variante(VarianteBase):
    idVariante: int