from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class CategoriaBase(BaseModel):
    nombre: str
    model_config = ConfigDict(from_attributes=True)

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(CategoriaBase):
    nombre: Optional[str] = None
    
class CategoriaRead(CategoriaBase):
    id_categoria: int
    model_config = ConfigDict(from_attributes=True)