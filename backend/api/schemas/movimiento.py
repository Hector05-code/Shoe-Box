from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TipoMovimientoEnum(str, Enum):
    entrada = "Entrada"
    salida = "Salida"
    ajuste = "Ajuste"
    devolucion = "Devolucion"

class MovimientoBase(BaseModel):
    cantidad: int = Field(gt=0)
    tipo_movimiento: TipoMovimientoEnum
    
    model_config = ConfigDict(from_attributes=True)

class MovimientoCreate(MovimientoBase):
    id_variante: int
    id_empleado: int
    fecha: Optional[datetime] = None
    
class MovimientoUpdate(BaseModel):
    cantidad: Optional[int] = None
    tipo_movimiento: Optional[TipoMovimientoEnum] = None

class MovimientoRead(MovimientoBase):
    id_movimiento: int
    id_variante: int
    id_empleado: int
    fecha: datetime
    
    model_config = ConfigDict(from_attributes=True)