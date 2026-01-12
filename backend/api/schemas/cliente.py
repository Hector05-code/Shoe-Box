from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    telefono: str = Field(max_length=45)
    direccion: str = Field(max_length=255)
    
    model_config = ConfigDict(from_attributes=True)

class ClienteCreate(ClienteBase):
    id_cliente_ci: int = Field(gt=0) #REVISAR ...
    
class ClienteUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=45)
    direccion: Optional[str] = Field(None, max_length=255)

class ClienteRead(ClienteBase):
    id_cliente_ci: int