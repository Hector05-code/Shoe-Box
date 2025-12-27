from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class ProductoBase(BaseModel):
    nombre: str
    marca: str
    categoria: str
    precio_venta: Decimal

class ProductoCreate(ProductoBase):
    id_producto: int
    
class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    marca: Optional[str] = None
    categoria: Optional[str] = None
    precio_venta: Optional[Decimal] = None

class Producto(ProductoBase):
    id_producto: int

    class Config:
        orm_mode = True
        json = {Decimal:lambda x:float(x)}
