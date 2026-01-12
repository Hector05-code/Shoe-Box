from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from schemas.help_color import ColorRead
from schemas.help_talla import TallaRead

class VarianteBase(BaseModel):
    barcode: str = Field(max_length=50)
    stock_actual: int = Field(default=0, ge=0)
    
    model_config = ConfigDict(from_attributes=True)

class VarianteCreate(VarianteBase):
    #idVariante: int si no es autoincremental
    id_color: int
    id_talla: int

class VarianteCreateSuelta(VarianteBase):
    id_producto: int
    
class VarianteUpdate(BaseModel):
    barcode: Optional[str] = Field(None, max_length=50)
    id_color: Optional[int] = None
    id_talla: Optional[int] = None
    stock_actual: Optional[int] = Field(None, ge=0)

class VarianteRead(VarianteBase):
    id_variante: int
    id_producto: int
    color_rel: ColorRead
    talla_rel: TallaRead
    
    model_config = ConfigDict(from_attributes=True)