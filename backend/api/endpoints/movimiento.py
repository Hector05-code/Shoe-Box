from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from modelos.movimiento import Movimiento as MovimientoModel, TipoMovimientoEnum
from schemas.movimiento import MovimientoRead
from modelos.variante import Variante as VarianteModel
from schemas.movimiento import MovimientoAjuste
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual
from utilidades.pin import requerir_permiso_gerente

endpoint = APIRouter(prefix="/movimientos", tags=["Movimientos (Historial)"])

# LEER TODOS (HISTORIAL + FILTROS)
@endpoint.get("/", response_model=List[MovimientoRead])
def consultar_historial(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    tipo: Optional[TipoMovimientoEnum] = None,
    id_variante: Optional[int] = None,
    _: EmpleadoRead = Depends(get_usuario_actual)
):
    query = db.query(MovimientoModel).options(
        joinedload(MovimientoModel.empleado_rel),
        joinedload(MovimientoModel.variante_rel)
    )

    if tipo:
        query = query.filter(MovimientoModel.tipo_movimiento == tipo)
    
    if id_variante:
        query = query.filter(MovimientoModel.id_variante == id_variante)

    movimientos = query.order_by(MovimientoModel.fecha.desc()).offset(skip).limit(limit).all()
    
    return movimientos

# REALIZAR AJUSTE DE INVENTARIO (PÉRDIDA, OTROS CASOS)
@endpoint.post("/ajuste", status_code=status.HTTP_201_CREATED)
def realizar_ajuste_inventario(
    ajuste: MovimientoAjuste, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
    autorizado: bool = Depends(requerir_permiso_gerente)
):

    variante = db.query(VarianteModel).filter(VarianteModel.id_variante == ajuste.id_variante).first()
    if not variante:
        raise HTTPException(status_code=404, detail="Variante no encontrada")

    stock_sistema = variante.stock_actual
    stock_real = ajuste.cantidad_real_fisica
    diferencia = stock_real - stock_sistema

    if diferencia == 0:
        return {"mensaje": "El stock físico coincide con el sistema. No se generaron movimientos."}

    variante.stock_actual = stock_real 

    nuevo_movimiento = MovimientoModel(
        id_variante=ajuste.id_variante,
        tipo_movimiento=TipoMovimientoEnum.AJUSTE,
        cantidad=diferencia,
        fecha=datetime.now(),
        id_empleado=usuario_actual.id_empleado,
        motivo=ajuste.motivo + f" (Sistema: {stock_sistema} -> Real: {stock_real})",
        stock_resultante=stock_real
    )

    db.add(nuevo_movimiento)
    db.add(variante)
    db.commit()
    
    accion = "Aumentó" if diferencia > 0 else "Disminuyó"
    return {
        "mensaje": f"Ajuste realizado. Se {accion} el stock en {abs(diferencia)} unidades.",
        "stock_nuevo": variante.stock_actual
    }