from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime
from decimal import Decimal
from modelos.venta import Venta as VentaModel
from modelos.detalle_venta import DetalleVenta as DetalleVentaModel
from modelos.variante import Variante as VarianteModel
from modelos.movimiento import Movimiento as MovimientoModel, TipoMovimientoEnum
from modelos.configuracion import Configuracion as ConfiguracionModel
from schemas.venta import VentaCreate, VentaRead, Devolucion, MetodoPagoEnum
from schemas.empleado import EmpleadoRead 
from utilidades.login import get_db, get_usuario_actual
from utilidades.pin import requerir_permiso_gerente

endpoint = APIRouter(prefix="/ventas", tags=["Ventas (Facturación)"])

# LEER TODOS
@endpoint.get("/", response_model=List[VentaRead])
def listar_ventas(db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    ventas = db.query(VentaModel).options(
        joinedload(VentaModel.cliente_rel),
        joinedload(VentaModel.empleado_rel)
    ).order_by(VentaModel.fecha.desc()).all()
    return ventas

# LEER UNO
@endpoint.get("/{id}", response_model=VentaRead)
def obtener_venta(id: int, db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    venta = db.query(VentaModel).options(
        joinedload(VentaModel.cliente_rel),
        joinedload(VentaModel.empleado_rel),
        joinedload(VentaModel.detalles).joinedload(DetalleVentaModel.variante_rel)
    ).filter(VentaModel.id_venta == id).first()

    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

# POST
@endpoint.post("/", response_model=VentaRead, status_code=status.HTTP_201_CREATED)
def crear_venta(
    venta_in: VentaCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    config = db.query(ConfiguracionModel).first()
    if not config:
        raise HTTPException(status_code=500, detail="Configuración no encontrada.")
        
    tasa_actual = config.tasa_dolar
    pct_iva = config.iva_porcentaje   
    pct_igtf = config.igtf_porcentaje 

    acumulado_subtotal_usd = Decimal(0)
    acumulado_iva_usd = Decimal(0)
    
    objetos_detalle_para_guardar = [] 
    
    for item in venta_in.items: 
        
        variante = db.query(VarianteModel).filter(VarianteModel.id_variante == item.id_variante).first()
        
        if not variante:
            raise HTTPException(status_code=404, detail=f"Variante ID {item.id_variante} no existe.")
        
        if variante.stock_actual < item.cantidad:
            raise HTTPException(
                status_code=400, 
                detail=f"Stock insuficiente para {variante.producto_rel.nombre}. Pedido: {item.cantidad}, Disponible: {variante.stock_actual}"
            )

        if variante.precio_venta_usd_esp is not None:
            precio_real = variante.precio_venta_usd_esp
        else:
            precio_real = variante.producto_rel.precio_venta_usd

        subtotal_linea = precio_real * item.cantidad
        acumulado_subtotal_usd += subtotal_linea
        
        if variante.producto_rel.aplica_iva:
            acumulado_iva_usd += (subtotal_linea * pct_iva)
            
        precio_en_bs = precio_real * tasa_actual

        detalle_obj = DetalleVentaModel(
            id_variante=item.id_variante,
            cantidad=item.cantidad,
            precio_unitario_usd_snapshot=precio_real,
            precio_und=precio_en_bs,
            cant_devuelta=0
        )
        
        movimiento_obj = MovimientoModel(
            id_variante=item.id_variante,
            id_empleado=usuario_actual.id_empleado,
            cantidad=item.cantidad,
            tipo_movimiento=TipoMovimientoEnum.SALIDA,
            fecha=datetime.now(),
            stock_resultante=variante.stock_actual - item.cantidad 
        )


        variante.stock_actual -= item.cantidad
        
        objetos_detalle_para_guardar.append((detalle_obj, movimiento_obj))


    porcentaje_decimal = Decimal(venta_in.descuento_porcentaje or 0)
    monto_descuento_usd = acumulado_subtotal_usd * porcentaje_decimal
    
    base_imponible_usd = acumulado_subtotal_usd - monto_descuento_usd
    total_a_pagar_base_usd = base_imponible_usd + acumulado_iva_usd
    
    if venta_in.abono_divisa_usd > total_a_pagar_base_usd:
         pass

    monto_igtf_usd = venta_in.abono_divisa_usd * pct_igtf
    total_final_usd = total_a_pagar_base_usd + monto_igtf_usd
    total_final_bs = total_final_usd * tasa_actual

    try:
        nueva_venta = VentaModel(
            id_cliente=venta_in.id_cliente,
            id_empleado=usuario_actual.id_empleado,
            fecha=datetime.now(),
            tasa_dolar_snapshot=tasa_actual,
            subtotal_usd=acumulado_subtotal_usd,
            descuento_porcentaje=venta_in.descuento_porcentaje,
            motivo_descuento=venta_in.motivo_descuento,
            monto_iva_usd=acumulado_iva_usd,
            monto_igtf_usd=monto_igtf_usd,
            total_venta_usd=total_final_usd,
            total_venta_bolivares=total_final_bs
        )
        db.add(nueva_venta)
        db.flush()

        for detalle, movimiento in objetos_detalle_para_guardar:
            detalle.id_venta = nueva_venta.id_venta
            movimiento.motivo = f"Venta #{nueva_venta.id_venta}"
            
            db.add(detalle)
            db.add(movimiento)

        db.commit()
        db.refresh(nueva_venta)
        return nueva_venta

    except Exception as e:
        db.rollback()
        print(f"Error creando venta: {e}") 
        raise HTTPException(status_code=500, detail=f"Error procesando la venta: {str(e)}")

# DELETE
@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def anular_venta(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
    autorizado: bool = Depends(requerir_permiso_gerente)
):

    venta = db.query(VentaModel).filter(VentaModel.id_venta == id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    try:
        for detalle in venta.detalles:
            variante = db.query(VarianteModel).get(detalle.id_variante)
            if variante:
                variante.stock_actual += detalle.cantidad
                
                mov_devolucion = MovimientoModel(
                    id_variante=detalle.id_variante,
                    id_empleado=usuario_actual.id_empleado,
                    cantidad=detalle.cantidad,
                    tipo_movimiento=TipoMovimientoEnum.DEVOLUCION,
                    motivo=f"Anulación Venta #{id}"
                )
                db.add(mov_devolucion)

        db.delete(venta)
        db.commit()
        return

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@endpoint.post("/devolucion", status_code=status.HTTP_200_OK)
def procesar_devolucion(
    solicitud: Devolucion,
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):

    detalle_db = db.query(DetalleVentaModel).filter(
        DetalleVentaModel.id_detalle_venta == solicitud.id_detalle_venta
    ).first()

    if not detalle_db:
        raise HTTPException(status_code=404, detail="El detalle de venta no existe.")

    cantidad_disponible_para_devolver = detalle_db.cantidad - detalle_db.cant_devuelta
    
    if solicitud.cant_devuelta > cantidad_disponible_para_devolver:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede devolver {solicitud.cant_devuelta}. Solo quedan {cantidad_disponible_para_devolver} habilitados para devolución en esta venta."
        )

    try:
        variante_db = db.query(VarianteModel).filter(
            VarianteModel.id_variante == detalle_db.id_variante
        ).first()

        variante_db.stock_actual += solicitud.cant_devuelta

        nuevo_movimiento = MovimientoModel(
            id_variante=variante_db.id_variante,
            id_empleado=usuario_actual.id_empleado,
            cant_devuelta=solicitud.cant_devuelta,
            tipo_movimiento=TipoMovimientoEnum.DEVOLUCION,
            motivo=f"Devolución Venta #{detalle_db.id_venta} - {solicitud.motivo}"
        )
        db.add(nuevo_movimiento)

        detalle_db.cant_devuelta += solicitud.cantidad_devuelta

        db.commit()
        return {"mensaje": "Devolución procesada exitosamente", "nuevo_stock": variante_db.stock_actual}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))