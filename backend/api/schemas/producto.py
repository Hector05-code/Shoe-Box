from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional, List
from schemas.variante import VarianteCreate, VarianteRead
from schemas.help_categoria import CategoriaRead

class ProductoBase(BaseModel):
    nombre: str = Field(max_length=145)
    marca: str = Field(max_length=45)
    precio_venta: Decimal = Field(gt=0)

class ProductoCreate(ProductoBase):
    id_categoria: int
    variantes: List[VarianteCreate]
    
class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=145)
    marca: Optional[str] = Field(None, max_length=45)
    id_categoria: Optional[str] = None
    precio_venta: Optional[Decimal] = Field(None, gt=0)

class ProductoRead(ProductoBase):
    id_producto: int
    categoria: CategoriaRead
    variantes: List[VarianteRead]
    estatus: bool
    
    model_config = ConfigDict(from_attributes=True)
