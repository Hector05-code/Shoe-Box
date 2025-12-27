from pydantic import BaseModel
from typing import Optional

class ClienteBase(BaseModel):
    Nombre: str
    Apellido: str
    Telefono: str
    Direccion: str

class ClienteCreate(ClienteBase):
    id_Cliente_CI: int
    
class ClienteUpdate(BaseModel):
    Nombre: Optional[str] = None
    Apellido: Optional[str] = None
    Telefono: Optional[str] = None
    Direccion: Optional[str] = None

class Cliente(ClienteBase):
    id_Cliente_CI: int