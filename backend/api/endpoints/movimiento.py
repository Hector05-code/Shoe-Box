from fastapi import APIRouter, Depends #Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

from config_db import sesion_local
from modelos.movimiento import Movimiento as MovimientoModel, TipoMovimientoEnum
from schemas.movimiento import MovimientoRead

endpoint = APIRouter(prefix="/movimientos", tags=["Movimientos (Kardex/Historial)"])

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

@endpoint.get("/", response_model=List[MovimientoRead])
def consultar_historial(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[TipoMovimientoEnum] = None, # Filtro opcional por tipo (ENTRADA/SALIDA)
    id_variante: Optional[int] = None # Filtro opcional para ver historial de una sola camisa
):
    # """
    # Consulta el historial de movimientos de inventario.
    # Permite filtrar por Tipo (ej: solo ver AJUSTES) o por Producto.
    # """
    query = db.query(MovimientoModel).options(
        joinedload(MovimientoModel.empleado_rel),
        joinedload(MovimientoModel.variente_rel)
    )

    # Filtros dinámicos
    if tipo:
        query = query.filter(MovimientoModel.tipo_movimiento == tipo)
    
    if id_variante:
        query = query.filter(MovimientoModel.id_variante == id_variante)

    # Ordenar por el más reciente
    movimientos = query.order_by(MovimientoModel.fecha.desc()).offset(skip).limit(limit).all()
    
    return movimientos