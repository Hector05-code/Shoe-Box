from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class Tipo_Movimiento(str, Enum):
    Entrada = "Entrada"
    Salida = "Salida"

class MovimientoBase(BaseModel):
    cantidad: int
    fecha: datetime
    id_variante: int
    TipoMovimiento: Tipo_Movimiento
    movimiento_Empleado: int

class MovimientoCreate(MovimientoBase):
    id_Movimiento: int
    
class MovimientoUpdate(BaseModel):
    cantidad: Optional[int] = None
    fecha: Optional[datetime] = None
    id_variante: Optional[int] = None
    TipoMovimiento: Optional[Tipo_Movimiento] = None
    movimiento_Empleado: Optional[int] = None

class Movimiento(MovimientoBase):
    id_Movimiento: int