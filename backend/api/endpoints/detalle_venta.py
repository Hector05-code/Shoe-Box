from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session #joinedload
from typing import List

from config_db import sesion_local
from modelos.detalle_venta import DetalleVenta as DetalleVentaModel
from schemas.detalle_venta import DetalleVentaRead

endpoint = APIRouter(prefix="/detalles-venta", tags=["Detalles de Ventas"])

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

@endpoint.get("/", response_model=List[DetalleVentaRead])
def listar_todos_los_items_vendidos(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return db.query(DetalleVentaModel).offset(skip).limit(limit).all()

@endpoint.get("/por-venta/{id_venta}", response_model=List[DetalleVentaRead])
def listar_items_de_una_venta(id_venta: int, db: Session = Depends(get_db)):
    return db.query(DetalleVentaModel).filter(DetalleVentaModel.id_venta == id_venta).all()