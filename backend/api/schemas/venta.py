from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from enum import Enum
from schemas.cliente import ClienteRead
from schemas.empleado import EmpleadoRead
from schemas.detalle_venta import DetalleVentaRead, DetalleVentaCreate

class MetodoPagoEnum(str, Enum):
    EFECTIVO_USD = "Efectivo USD"
    ZELLE = "ZELLE"
    PAGO_MOVIL = "Pago Móvil"
    PUNTO_VENTA = "Punto de Venta"
    EFECTIVO_BS = "Efectivo Bs."
    MIXTO = "Mixto"

class VentaBase(BaseModel):
    fecha: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class VentaCreate(VentaBase):
    id_cliente: int
    id_empleado: int
    metodo_pago: MetodoPagoEnum
    items: List[DetalleVentaCreate]
    abono_divisa_usd: Optional[Decimal] = Field(0, ge=0)
    descuento_porcentaje: Decimal = Field(default=0.0, ge=0, le=1)
    motivo_descuento: Optional[str] = Field(default=None, description="Obligatorio si hay descuento")
    
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
    
    tasa_dolar_snapshot: Decimal
    subtotal_usd: Decimal
    monto_iva_usd: Decimal
    monto_igtf_usd: Decimal
    total_venta_usd: Decimal
    total_venta_bolivares: Decimal
    
    detalles: List[DetalleVentaRead]
    
    model_config = ConfigDict(from_attributes=True)

class Devolucion(BaseModel):
    id_detalle_venta: int
    cant_devuelta: int = Field(gt=0)
    motivo: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)