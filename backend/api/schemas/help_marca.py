from pydantic import BaseModel, ConfigDict
from typing import Optional

class MarcaBase(BaseModel):
    nombre: str
    
    model_config = ConfigDict(from_attributes=True)

class MarcaCreate(MarcaBase):
    pass

class MarcaUpdate(BaseModel):
    nombre: Optional[str] = None
    estatus: Optional[bool] = None

class MarcaRead(MarcaBase):
    id_marca: int
    estatus: bool

    model_config = ConfigDict(from_attributes=True)