from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional, List
from schemas.variante import VarianteCreate, VarianteRead
from schemas.help_categoria import CategoriaRead
from schemas.help_marca import MarcaRead

class ProductoBase(BaseModel):
    nombre: str = Field(max_length=145)
    costo_usd: Decimal = Field(gt=0)
    precio_venta_usd: Decimal = Field(gt=0)
    aplica_iva: bool

class ProductoCreate(ProductoBase):
    id_categoria: int
    id_marca: int
    variantes: List[VarianteCreate]
    
class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=145)
    id_marca: Optional[int] = None
    id_categoria: Optional[int] = None
    costo_usd: Optional[Decimal] = Field(None, gt=0)
    precio_venta_usd: Optional[Decimal] = Field(None, gt=0)
    estatus: Optional[bool] = None

class ProductoRead(ProductoBase):
    id_producto: int
    categoria_rel: CategoriaRead
    marca_rel: Optional[MarcaRead]
    variantes: List[VarianteRead]
    estatus: bool
    
    model_config = ConfigDict(from_attributes=True)
