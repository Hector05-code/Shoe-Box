from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

class ItemRecepcionCreate(BaseModel):
    id_variante: int
    cantidad: int = Field(gt=0)
    costo_unitario_usd: float = Field(ge=0)

class RecepcionCreate(BaseModel):
    numero_factura_proveedor: Optional[str] = None
    proveedor_nombre: Optional[str] = None
    observaciones: Optional[str] = None
    items: List[ItemRecepcionCreate]

class RecepcionRead(BaseModel):
    id_recepcion: int
    fecha: datetime
    numero_factura_proveedor: Optional[str]
    total_costo_lote_usd: float
    cantidad_items_procesados: int

    model_config = ConfigDict(from_attributes=True)