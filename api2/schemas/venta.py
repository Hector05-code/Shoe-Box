from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from datetime import datetime

class VentaBase(BaseModel):
    id_empleado: int
    id_cliente: int
    fecha: datetime
    total: Decimal

class VentaCreate(VentaBase):
    id_venta: int
    
class VentaUpdate(BaseModel):
    id_empleado: Optional[int] = None
    id_cliente: Optional[int] = None
    fecha: Optional[datetime] = None
    total: Optional[Decimal] = None

class Venta(VentaBase):
    id_venta: int

    class Config:
        orm_mode = True
        json = {Decimal:lambda x:float(x)}