from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from modelos.empleado import EmpleadoFuncionEnum

class EmpleadoBase(BaseModel):
    nombre: str = Field(max_length=100)
    apellido: str = Field(max_length=100)
    telefono: str = Field(max_length=45)
    direccion: str = Field(max_length=255)
    usuario: str = Field(max_length=50)
    funcion: EmpleadoFuncionEnum
    
    model_config = ConfigDict(from_attributes=True)

class EmpleadoCreate(EmpleadoBase):
    id_empleado: int
    contrasena: str = Field(min_length=6, max_length=255)
    
class EmpleadoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    apellido: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=45)
    usuario: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=255)
    funcion: Optional[EmpleadoFuncionEnum] = None
    contrasena: Optional[str] = Field(None, max_length=255)
    estatus: Optional[bool] = None

class EmpleadoRead(EmpleadoBase):
    id_empleado: int
    estatus: bool