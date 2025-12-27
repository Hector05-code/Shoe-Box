from pydantic import BaseModel
from typing import Optional

class EmpleadoBase(BaseModel):
    Nombre: str
    Apellido: str
    Telefono: str
    Usuario: str
    Contraseña: str
    Funcion: str

class EmpleadoCreate(EmpleadoBase):
    id_Empleado: int
    
class EmpleadoUpdate(BaseModel):
    Nombre: Optional[str] = None
    Apellido: Optional[str] = None
    Telefono: Optional[str] = None
    Usuario: Optional[str] = None
    Contraseña: Optional[str] = None
    Funcion: Optional[str] = None

class Empleado(EmpleadoBase):
    id_Empleado: int