from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from decimal import Decimal
from schemas.help_color import ColorRead
from schemas.help_talla import TallaRead

class VarianteBase(BaseModel):
    barcode: Optional[str] = Field(max_length=50)
    stock_actual: int = Field(default=0, ge=0)
    stock_minimo: int = Field(default=5, ge=0)
    costo_usd_esp: Optional[Decimal] = None
    precio_venta_usd_esp: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)

class VarianteCreate(VarianteBase):
    id_producto: int
    id_color: int
    id_talla: int
    stock_actual: int = Field(default=0, ge=0)
    
class VarianteUpdate(BaseModel):
    barcode: Optional[str] = Field(None, max_length=50)
    id_color: Optional[int] = None
    id_talla: Optional[int] = None
    stock_actual: Optional[int] = Field(None, ge=0)
    stock_minimo: Optional[int] = Field(None, ge=0)
    costo_usd_esp: Optional[float] = None
    precio_venta_usd_esp: Optional[float] = None
    estatus: Optional[bool] = None

class VarianteRead(VarianteBase):
    id_variante: int
    id_producto: int
    color_rel: ColorRead
    talla_rel: TallaRead
    stock_actual: int
    estatus: bool
    
    model_config = ConfigDict(from_attributes=True)