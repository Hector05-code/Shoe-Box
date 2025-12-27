from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.variante import Variante
from modelos.movimiento import Movimiento
from schemas.movimiento import MovimientoCreate, MovimientoUpdate

endpoint = APIRouter(prefix="/inventario", tags=["inventario"])

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()


@endpoint.get("/stock/{id_variante}")
def consultar_stock(id_variante: int, db: Session = Depends(get_db)):
    try:
        variante = db.query(Variante).filter(Variante.idVariante == id_variante).first()
        if not variante:
            raise HTTPException(status_code=404, detail="Variante no encontrada")
        return {"variante": variante.idVariante, "stock_actual": variante.stock_actual}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


@endpoint.post("/entrada")
def registrar_entrada(movimiento: MovimientoCreate, db: Session = Depends(get_db)):
    try:
        variante = db.query(Variante).filter(Variante.idVariante == movimiento.id_variante).first()
        if not variante:
            raise HTTPException(status_code=404, detail="Variante no encontrada")

        nuevo_mov = Movimiento(
            id_variante=variante.idVariante,
            cantidad=movimiento.cantidad,
            fecha=movimiento.fecha,
            TipoMovimiento="Entrada",
            movimiento_Empleado=movimiento.movimiento_Empleado
        )
        db.add(nuevo_mov)

        variante.stock_actual += movimiento.cantidad
        db.commit()

        return {"mensaje": "Entrada registrada", "stock_actual": variante.stock_actual}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


@endpoint.post("/salida")
def registrar_salida(movimiento: MovimientoCreate, db: Session = Depends(get_db)):
    try:
        variante = db.query(Variante).filter(Variante.idVariante == movimiento.id_variante).first()
        if not variante:
            raise HTTPException(status_code=404, detail="Variante no encontrada")

        if variante.stock_actual < movimiento.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")

        nuevo_mov = Movimiento(
            id_variante=variante.idVariante,
            cantidad=movimiento.cantidad,
            fecha=movimiento.fecha,
            TipoMovimiento="Salida",
            movimiento_Empleado=movimiento.movimiento_Empleado
        )
        db.add(nuevo_mov)

        variante.stock_actual -= movimiento.cantidad
        db.commit()

        return {"mensaje": "Salida registrada", "stock_actual": variante.stock_actual}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


@endpoint.put("/actualizar/{id_movimiento}")
def actualizar_movimiento(id_movimiento: int, movimiento: MovimientoUpdate, db: Session = Depends(get_db)):
    try:
        mov = db.query(Movimiento).filter(Movimiento.id_Movimiento == id_movimiento).first()
        if not mov:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")

        mov.cantidad = movimiento.cantidad
        mov.fecha = movimiento.fecha
        mov.id_variante = movimiento.id_variante
        mov.TipoMovimiento = movimiento.TipoMovimiento
        mov.movimiento_Empleado = movimiento.movimiento_Empleado

        db.commit()
        return {"mensaje": "Movimiento actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")