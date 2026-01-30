from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime
from modelos.variante import Variante as VarianteModel
from modelos.producto import Producto as ProductoModel
from modelos.movimiento import Movimiento as MovimientoModel, TipoMovimientoEnum
from schemas.variante import VarianteRead, VarianteUpdate, VarianteCreate 
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual

endpoint = APIRouter(prefix="/variantes", tags=["Variantes (Inventario)"])

# LEER TODOS
@endpoint.get("/", response_model=List[VarianteRead])
def listar_variantes(
    skip: int = 0, 
    limit: int = 100, 
    mostrar_inactivos: bool = False,
    db: Session = Depends(get_db),
    _: EmpleadoRead = Depends(get_usuario_actual)
):

    query = db.query(VarianteModel).options(
        joinedload(VarianteModel.color_rel),
        joinedload(VarianteModel.talla_rel),
        joinedload(VarianteModel.producto_rel)
    )

    if not mostrar_inactivos:
        query = query.filter(VarianteModel.estatus == True)
        
    variantes = query.offset(skip).limit(limit).all()
    
    return variantes

# LEER UNO
@endpoint.get("/{id}", response_model=VarianteRead)
def obtener_variante(
    id: int, 
    db: Session = Depends(get_db),
    _: EmpleadoRead = Depends(get_usuario_actual)
    ):
    
    variante = db.query(VarianteModel).options(
        joinedload(VarianteModel.color_rel),
        joinedload(VarianteModel.talla_rel),
        joinedload(VarianteModel.producto_rel)
    ).filter(VarianteModel.id_variante == id).first()
    
    if not variante:
        raise HTTPException(status_code=404, detail="Variante no encontrada")
        
    return variante

# POST
@endpoint.post("/", response_model=VarianteRead, status_code=status.HTTP_201_CREATED)
def crear_variante_suelta(
    variante_in: VarianteCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):

    producto_padre = db.query(ProductoModel).get(variante_in.id_producto)
    if not producto_padre:
        raise HTTPException(status_code=404, detail="El producto padre no existe.")

    existe_combinacion = db.query(VarianteModel).filter(
        VarianteModel.id_producto == variante_in.id_producto,
        VarianteModel.id_color == variante_in.id_color,
        VarianteModel.id_talla == variante_in.id_talla,
        VarianteModel.estatus == True
    ).first()
    
    if existe_combinacion:
        raise HTTPException(status_code=400, detail="Esta combinación (Producto + Color + Talla) ya existe.")

    barcode_final = variante_in.barcode
    if not barcode_final:
        barcode_final = f"P{variante_in.id_producto}-C{variante_in.id_color}-T{variante_in.id_talla}"
    else:
        existe_barcode = db.query(VarianteModel).filter(VarianteModel.barcode == barcode_final).first()
        if existe_barcode:
             raise HTTPException(status_code=400, detail=f"El Código de barras '{barcode_final}' ya está en uso.")

    try:
        nueva_variante = VarianteModel(
            id_producto=variante_in.id_producto,
            id_talla=variante_in.id_talla,
            id_color=variante_in.id_color,
            barcode=barcode_final,
            stock_minimo=variante_in.stock_minimo,
            stock_actual=variante_in.stock_actual,
            costo_usd_esp=variante_in.costo_usd_esp,
            precio_venta_usd_esp=variante_in.precio_venta_usd_esp,
            estatus=True
        )
        
        db.add(nueva_variante)
        db.flush()
        
        if variante_in.stock_actual > 0:
            movimiento = MovimientoModel(
                id_variante=nueva_variante.id_variante,
                id_empleado=usuario_actual.id_empleado,
                cantidad=variante_in.stock_actual,
                tipo_movimiento=TipoMovimientoEnum.ENTRADA,
                fecha=datetime.now(),
                motivo="Inventario Inicial (Creación de Variante)",
                stock_resultante=variante_in.stock_actual
            )
            db.add(movimiento)

        db.commit()
        db.refresh(nueva_variante)
        return nueva_variante

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# PUT
@endpoint.put("/{id_variante}", response_model=VarianteRead)
def actualizar_variante(
    id_variante: int, 
    variante_update: VarianteUpdate, 
    db: Session = Depends(get_db),
    usuario_actual : EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "GERENTE":
        raise HTTPException(status_code=403, detail="No tienes permisos para esta función.")

    variante_db = db.query(VarianteModel).filter(VarianteModel.id_variante == id_variante).first()
    if not variante_db:
        raise HTTPException(status_code=404, detail="Variante no encontrada")

    datos_nuevos = variante_update.model_dump(exclude_unset=True)

    stock_nuevo = datos_nuevos.get("stock_actual")
    
    if stock_nuevo is not None and stock_nuevo != variante_db.stock_actual:
        diferencia = stock_nuevo - variante_db.stock_actual
        
        accion = "Aumentó" if diferencia > 0 else "Disminuyó"
        
        movimiento_ajuste = MovimientoModel(
            id_variante=id_variante,
            id_empleado=usuario_actual.id_empleado,
            cantidad=diferencia,
            tipo_movimiento=TipoMovimientoEnum.AJUSTE,
            fecha=datetime.now(),
            motivo=f"Corrección manual desde panel: {accion} {abs(diferencia)} unidades.",
            stock_resultante=stock_nuevo
        )
        db.add(movimiento_ajuste)

    for key, value in datos_nuevos.items():
        setattr(variante_db, key, value)

    try:
        db.commit()
        db.refresh(variante_db)
        return variante_db
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: Posible Código de barras o dato duplicado.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# DELETE
@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_variante(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):

    if usuario_actual.funcion.value != "GERENTE":
        raise HTTPException(status_code=403, detail="No tiene permisos para esta función.")

    variante_db = db.query(VarianteModel).filter(VarianteModel.id_variante == id).first()
    
    if not variante_db:
        raise HTTPException(status_code=404, detail="Variante no encontrada")

    try:
        db.delete(variante_db)
        db.commit()
        
    except IntegrityError:
        db.rollback()
        
        variante_db.estatus = False 
        
        db.add(variante_db)
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"Error inesperado al borrar variante: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    return None