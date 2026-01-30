from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import date

class AlertaStockRead(BaseModel):
    producto: str
    variante: str
    barcode: str
    stock_actual: int
    stock_minimo: int

class ReporteVentasRead(BaseModel):
    rango_fecha: str
    cantidad_ventas: int
    total_facturado_usd: Decimal
    total_facturado_bs: Decimal
    
class TopCategoriaRead(BaseModel):
    categoria: str
    unidades_vendidas: int
    dinero_generado_usd: Decimal