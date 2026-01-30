from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from modelos.detalle_venta import DetalleVenta as DetalleVentaModel
from schemas.detalle_venta import DetalleVentaRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual

endpoint = APIRouter(prefix="/detalles-venta", tags=["Detalles de Ventas"])

# LEER ITEMS VENDIDOS
@endpoint.get("/", response_model=List[DetalleVentaRead])
def listar_todos_los_items_vendidos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    _: EmpleadoRead = Depends(get_usuario_actual)
):
    return db.query(DetalleVentaModel).offset(skip).limit(limit).all()

# LEER ITEMS DE UNA VENTA
@endpoint.get("/por-venta/{id_venta}", response_model=List[DetalleVentaRead])
def listar_items_de_una_venta(id_venta: int, db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    return db.query(DetalleVentaModel).filter(DetalleVentaModel.id_venta == id_venta).all()