from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class Detalle_ventaBase(BaseModel):
    id_venta: int
    linea: str
    precio_venta: Decimal
    cantidad: int
    idvariante: int

class Detalle_ventaCreate(Detalle_ventaBase):
    id_Detalle_venta: int
    
class Detalle_ventaUpdate(BaseModel):
    id_venta: Optional[int] = None
    linea: Optional[str] = None
    precio_venta: Optional[Decimal] = None
    cantidad: Optional[int] = None
    idvariante: Optional[int] = None

class Detalle_venta(Detalle_ventaBase):
    id_Detalle_venta: int

    class Config:
        orm_mode = True
        json = {Decimal:lambda x:float(x)}