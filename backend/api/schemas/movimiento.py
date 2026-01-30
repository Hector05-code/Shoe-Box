from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from modelos.movimiento import TipoMovimientoEnum

class MovimientoBase(BaseModel):
    cantidad: int = Field(gt=0)
    tipo_movimiento: TipoMovimientoEnum
    motivo: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class MovimientoCreate(MovimientoBase):
    id_variante: int
    id_empleado: int
    fecha: Optional[datetime] = None
    stock_resultante: int
    
class MovimientoUpdate(BaseModel):
    cantidad: Optional[int] = None
    tipo_movimiento: Optional[TipoMovimientoEnum] = None

class MovimientoRead(MovimientoBase):
    id_movimiento: int
    id_variante: int
    id_empleado: int
    fecha: datetime
    stock_resultante: int
    
    model_config = ConfigDict(from_attributes=True)

class MovimientoAjuste(BaseModel):
    id_variante: int
    cantidad_real_fisica: int = Field(ge=0)
    motivo: str = Field(min_length=5)