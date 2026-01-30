from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional
from schemas.variante import VarianteRead

class DetalleVentaBase(BaseModel):
    cantidad: int = Field(gt=0)

    model_config = ConfigDict(from_attributes=True)

class DetalleVentaCreate(DetalleVentaBase):
    id_variante: int
    cantidad: int = Field(gt=0)
    
class DetalleVentaUpdate(BaseModel):
    cantidad: Optional[int] = Field(None, gt=0)


class DetalleVentaRead(DetalleVentaBase):
    id_detalle_venta: int
    id_venta: int
    id_variante: int
    precio_und: Decimal
    precio_unitario_usd_snapshot: Decimal
    subtotal_usd: Optional[Decimal]
    cant_devuelta: int
    
    variante_rel: VarianteRead
    model_config = ConfigDict(from_attributes=True)