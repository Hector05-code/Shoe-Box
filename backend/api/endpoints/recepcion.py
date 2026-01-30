from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from modelos.recepcion import Recepcion as RecepcionModel
from modelos.movimiento import Movimiento as MovimientoModel, TipoMovimientoEnum
from modelos.variante import Variante as VarianteModel
from schemas.recepcion import RecepcionCreate, RecepcionRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual

endpoint = APIRouter(prefix="/recepcion", tags=["Recepción de Mercancía"])

@endpoint.post("/", response_model=RecepcionRead, status_code=status.HTTP_201_CREATED)
def procesar_recepcion_lote(
    recepcion_in: RecepcionCreate,
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    nueva_recepcion = RecepcionModel(
        numero_factura_proveedor=recepcion_in.numero_factura_proveedor,
        proveedor_nombre=recepcion_in.proveedor_nombre,
        observaciones=recepcion_in.observaciones,
        id_empleado=usuario_actual.id_empleado,
        fecha=datetime.now(),
        total_costo_lote_usd=0.0 
    )
    
    db.add(nueva_recepcion)
    db.flush() 

    total_costo_acumulado = 0.0
    items_count = 0

    try:
        for item in recepcion_in.items:
            variante: VarianteModel = db.query(VarianteModel).filter(VarianteModel.id_variante == item.id_variante).first()
            
            if not variante:
                raise HTTPException(status_code=404, detail=f"Variante ID {item.id_variante} no encontrada.")

            if variante.producto_rel: 
                variante.producto_rel.costo_usd = item.costo_unitario_usd
            
            variante.stock_actual += item.cantidad
            
            nuevo_movimiento = MovimientoModel(
                id_variante=item.id_variante,
                id_empleado=usuario_actual.id_empleado,
                cantidad=item.cantidad, 
                tipo_movimiento=TipoMovimientoEnum.ENTRADA,
                fecha=datetime.now(),
                id_recepcion=nueva_recepcion.id_recepcion,
                motivo=f"Recepción Fact: {recepcion_in.numero_factura_proveedor or 'S/N'}", 
                stock_resultante=variante.stock_actual
            )
            
            db.add(nuevo_movimiento)
            
            total_costo_acumulado += (item.costo_unitario_usd * item.cantidad)
            items_count += 1

        nueva_recepcion.total_costo_lote_usd = total_costo_acumulado
        db.commit()
        db.refresh(nueva_recepcion)
        
        return {
            "id_recepcion": nueva_recepcion.id_recepcion,
            "fecha": nueva_recepcion.fecha,
            "numero_factura_proveedor": nueva_recepcion.numero_factura_proveedor,
            "total_costo_lote_usd": nueva_recepcion.total_costo_lote_usd,
            "cantidad_items_procesados": items_count
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error procesando recepción: {str(e)}")