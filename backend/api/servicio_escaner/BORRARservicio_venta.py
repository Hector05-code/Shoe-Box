from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.variante import Variante
from modelos.movimiento import Movimiento
from modelos.venta import Venta
from modelos.detalle_venta import Detalle_venta

endpoint = APIRouter(prefix="/ventas", tags=["ventas"])

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()


@endpoint.post("/registrar")
def registrar_venta(id_variante: int, cantidad: int, movimiento_Empleado: int, db: Session = Depends(get_db)):
    try:
        variante = db.query(Variante).filter(Variante.idVariante == id_variante).first()
        if not variante:
            raise HTTPException(status_code=404, detail="Variante no encontrada")

        if variante.stock_actual < cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente")

        # Crear venta
        nueva_venta = Venta()
        db.add(nueva_venta)
        db.flush()  # obtener id de la venta

        # Crear detalle de venta
        detalle = Detalle_venta(
            id_venta=nueva_venta.id_venta,
            id_variante=variante.idVariante,
            cantidad=cantidad,
            precio_unitario=variante.precio_venta
        )
        db.add(detalle)

        # Registrar movimiento de salida
        movimiento = Movimiento(
            id_variante=variante.idVariante,
            cantidad=cantidad,
            fecha=nueva_venta.fecha,  # puedes usar la fecha de la venta
            TipoMovimiento="Salida",
            movimiento_Empleado=movimiento_Empleado
        )
        db.add(movimiento)

        # Actualizar stock
        variante.stock_actual -= cantidad
        db.commit()

        return {
            "mensaje": "Venta registrada",
            "venta_id": nueva_venta.id_venta,
            "variante": variante.idVariante,
            "cantidad": cantidad,
            "stock_restante": variante.stock_actual
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")