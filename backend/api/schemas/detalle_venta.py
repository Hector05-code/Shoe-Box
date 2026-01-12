from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional
from schemas.variante import VarianteRead

class DetalleVentaBase(BaseModel):
    cantidad: int = Field(gt=0)
    precio_und: Decimal = Field(ge=0)
    #linea: Optional[str]
    model_config = ConfigDict(from_attributes=True)

class DetalleVentaCreate(DetalleVentaBase):
    id_variante: int
    
class DetalleVentaUpdate(BaseModel):
    cantidad: Optional[int] = Field(None, gt=0)
    precio_und: Optional[Decimal] = Field(None, ge=0)
    id_variante: Optional[int] = None
    #linea: Optional[str] = None

class DetalleVentaRead(DetalleVentaBase):
    id_detalle_venta: int
    id_venta: int
    id_variante: int
    cant_devuelta: int
    
    variante_rel: VarianteRead
    model_config = ConfigDict(from_attributes=True)