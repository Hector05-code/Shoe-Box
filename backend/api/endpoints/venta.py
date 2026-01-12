from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from config_db import sesion_local
# Modelos
from modelos.venta import Venta as VentaModel
from modelos.detalle_venta import DetalleVenta as DetalleVentaModel
from modelos.variante import Variante as VarianteModel
from modelos.movimiento import Movimiento as MovimientoModel, TipoMovimientoEnum
# Schemas
from schemas.venta import VentaCreate, VentaRead, Devolucion
from schemas.empleado import EmpleadoRead 
from utilidades.login import get_usuario_actual

endpoint = APIRouter(prefix="/ventas", tags=["Ventas (Facturación)"])

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

# Mock de Seguridad (Cualquier empleado puede vender)
# def get_usuario_actual():
#     class UsuarioMock:
#         id_empleado = 1
#         funcion = "Empleado" # Puede ser Empleado o Gerente
#     return UsuarioMock()


@endpoint.get("/", response_model=List[VentaRead])
def listar_ventas(db: Session = Depends(get_db)):
    # Usamos joinedload para traer cliente y empleado en una sola consulta
    # OJO: No traemos 'detalles' aquí para no sobrecargar la lista general.
    # Si quieres ver detalles, usa el GET por ID.
    ventas = db.query(VentaModel).options(
        joinedload(VentaModel.cliente_rel),
        joinedload(VentaModel.empleado_rel)
    ).order_by(VentaModel.fecha.desc()).all()
    return ventas


@endpoint.get("/{id}", response_model=VentaRead)
def obtener_venta(id: int, db: Session = Depends(get_db)):
    # Aquí SI traemos los detalles y la info de las variantes
    venta = db.query(VentaModel).options(
        joinedload(VentaModel.cliente_rel),
        joinedload(VentaModel.empleado_rel),
        joinedload(VentaModel.detalles).joinedload(DetalleVentaModel.variante_rel)
    ).filter(VentaModel.id_venta == id).first()

    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta


@endpoint.post("/", response_model=VentaRead, status_code=status.HTTP_201_CREATED)
def crear_venta(
    venta_in: VentaCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    # """
    # PROCESO CRÍTICO:
    # 1. Validar Stock de todos los items.
    # 2. Crear Venta.
    # 3. Crear Detalles.
    # 4. Restar Stock.
    # 5. Crear Movimiento (Kardex).
    # Todo en una sola transacción.
    # """
    try:
        # PASO 1: VALIDACIÓN DE STOCK (Pre-chequeo)
        # No queremos crear la venta si el item 5 de 10 falla.
        for item in venta_in.detalles:
            variante = db.query(VarianteModel).filter(VarianteModel.id_variante == item.id_variante).first()
            if not variante:
                raise HTTPException(status_code=404, detail=f"Variante ID {item.id_variante} no existe.")
            
            if variante.stock_actual < item.cantidad:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Stock insuficiente para {variante.sku}. Pedido: {item.cantidad}, Disponible: {variante.stock_actual}"
                )

        # PASO 2: CREAR CABECERA DE VENTA
        nueva_venta = VentaModel(
            id_cliente=venta_in.id_cliente,
            id_empleado=usuario_actual.id_empleado, # Usamos el del token, no el que envíe el front por seguridad
            total=venta_in.total
            # fecha se pone sola (default now)
        )
        db.add(nueva_venta)
        db.flush() # Obtenemos id_venta

        # PASO 3, 4 y 5: PROCESAR RENGLONES
        for item in venta_in.detalles:
            # Recuperamos variante (ya sabemos que existe y tiene stock)
            variante_db = db.query(VarianteModel).get(item.id_variante)

            # A. Crear Detalle
            nuevo_detalle = DetalleVentaModel(
                id_venta=nueva_venta.id_venta,
                id_variante=item.id_variante,
                cantidad=item.cantidad,
                precio_und=item.precio_und,
                # Guardamos el nombre "congelado" por si borran el producto mañana
            )
            db.add(nuevo_detalle)

            # B. Restar Stock
            variante_db.stock_actual -= item.cantidad
            
            # C. Registrar Movimiento (SALIDA)
            nuevo_movimiento = MovimientoModel(
                id_variante=item.id_variante,
                id_empleado=usuario_actual.id_empleado,
                cantidad=item.cantidad,
                tipo_movimiento=TipoMovimientoEnum.salida,
                referencia=f"Venta #{nueva_venta.id_venta}"
            )
            db.add(nuevo_movimiento)

        # PASO 6: CONFIRMAR
        db.commit()
        
        # Refrescar para devolver datos completos
        db.refresh(nueva_venta)
        return nueva_venta

    except HTTPException as e:
        # Si fue error de validación manual, lo relanzamos
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def anular_venta(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    # """
    # ANULACIÓN DE VENTA (Solo Gerentes).
    # Devuelve automáticamente el stock al inventario.
    # """
    if usuario_actual.funcion != "Gerente":
        raise HTTPException(status_code=403, detail="Solo Gerentes pueden anular ventas.")

    venta = db.query(VentaModel).filter(VentaModel.id_venta == id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")

    try:
        # DEVOLUCIÓN DE STOCK
        for detalle in venta.detalles:
            variante = db.query(VarianteModel).get(detalle.id_variante)
            if variante:
                # 1. Sumar Stock
                variante.stock_actual += detalle.cantidad
                
                # 2. Registrar Movimiento (DEVOLUCION)
                mov_devolucion = MovimientoModel(
                    id_variante=detalle.id_variante,
                    id_empleado=usuario_actual.id_empleado,
                    cantidad=detalle.cantidad,
                    tipo_movimiento=TipoMovimientoEnum.devolucion,
                    referencia=f"Anulación Venta #{id}"
                )
                db.add(mov_devolucion)

        # Borramos la venta (Cascade borrará los detalles, pero el stock ya se recuperó)
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
    # """
    # Procesa la devolución PARCIAL o TOTAL de un item de una venta.
    # 1. Aumenta Stock.
    # 2. Crea Movimiento 'DEVOLUCION'.
    # 3. Marca items como devueltos en DetalleVenta.
    # """
    
    # 1. Buscar el detalle de la venta original
    detalle_db = db.query(DetalleVentaModel).filter(
        DetalleVentaModel.id_detalle_venta == solicitud.id_detalle_venta
    ).first()

    if not detalle_db:
        raise HTTPException(status_code=404, detail="El detalle de venta no existe.")

    # 2. Validaciones de Seguridad
    # A. No devolver más de lo que se compró
    # B. No devolver lo que YA se devolvió antes
    cantidad_disponible_para_devolver = detalle_db.cantidad - detalle_db.cant_devuelta
    
    if solicitud.cant_devuelta > cantidad_disponible_para_devolver:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede devolver {solicitud.cant_devuelta}. Solo quedan {cantidad_disponible_para_devolver} habilitados para devolución en esta venta."
        )

    try:
        # 3. Recuperar la Variante (Inventario)
        variante_db = db.query(VarianteModel).filter(
            VarianteModel.id_variante == detalle_db.id_variante
        ).first()

        # 4. AUMENTAR STOCK
        variante_db.stock_actual += solicitud.cant_devuelta

        # 5. REGISTRAR MOVIMIENTO (Kardex)
        nuevo_movimiento = MovimientoModel(
            id_variante=variante_db.id_variante,
            id_empleado=usuario_actual.id_empleado,
            cantidad=solicitud.cant_devuelta,
            tipo_movimiento=TipoMovimientoEnum.devolucion, # Asegúrate de tener este Enum
            referencia=f"Devolución Venta #{detalle_db.id_venta} - {solicitud.motivo}"
        )
        db.add(nuevo_movimiento)

        # 6. ACTUALIZAR EL DETALLE (Marcar como devuelto)
        detalle_db.cant_devuelta += solicitud.cantidad

        db.commit()
        return {"mensaje": "Devolución procesada exitosamente", "nuevo_stock": variante_db.stock_actual}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))