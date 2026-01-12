from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from schemas.cliente import ClienteRead
from schemas.empleado import EmpleadoRead
from schemas.detalle_venta import DetalleVentaRead, DetalleVentaCreate

class VentaBase(BaseModel):
    fecha: Optional[datetime] = None
    total: Decimal = Field(ge=0)
    
    model_config = ConfigDict(from_attributes=True)

class VentaCreate(VentaBase):
    id_cliente: int
    id_empleado: int
    detalles: List[DetalleVentaCreate]
    
class VentaUpdate(BaseModel):
    id_empleado: Optional[int] = None
    id_cliente: Optional[int] = None
    fecha: Optional[datetime] = None
    total: Optional[Decimal] = Field(None, ge=0)

class VentaRead(VentaBase):
    id_venta: int
    id_cliente: int
    id_empleado: int
    fecha: datetime
    
    cliente_rel: ClienteRead
    empleado_rel: EmpleadoRead
    detalles: List[DetalleVentaRead]
    
    model_config = ConfigDict(from_attributes=True)

class Devolucion(BaseModel):
    id_detalle_venta: int
    cant_devuelta: int = Field(gt=0)
    motivo: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)