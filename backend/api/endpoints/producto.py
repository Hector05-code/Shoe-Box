from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime
from modelos.producto import Producto as ProductoModel
from modelos.variante import Variante as VarianteModel
from modelos.movimiento import Movimiento as MovimientoModel, TipoMovimientoEnum
from schemas.producto import ProductoCreate, ProductoUpdate, ProductoRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual

endpoint = APIRouter(prefix="/productos", tags=["Productos"])

# LEER TODOS
@endpoint.get("/", response_model=List[ProductoRead])
def listar_productos(db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual), mostrar_inactivos: bool = False):
    
    productos = db.query(ProductoModel).options(
            joinedload(ProductoModel.variantes).joinedload(VarianteModel.color_rel),
            joinedload(ProductoModel.variantes).joinedload(VarianteModel.talla_rel),
            joinedload(ProductoModel.categoria_rel),
            joinedload(ProductoModel.marca_rel))
    
    if not mostrar_inactivos:
        productos = productos.filter(ProductoModel.estatus == True)
        return productos

# LEER UNO
@endpoint.get("/{id}", response_model=ProductoRead)
def obtener_producto(id: int, db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    producto = db.query(ProductoModel).options(
        joinedload(ProductoModel.variantes).joinedload(VarianteModel.color_rel),
        joinedload(ProductoModel.variantes).joinedload(VarianteModel.talla_rel),
        joinedload(ProductoModel.categoria_rel),
        joinedload(ProductoModel.marca_rel)
    ).filter(ProductoModel.id_producto == id).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# POST
@endpoint.post("/", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto_completo(
    producto_in: ProductoCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    try:
        producto_data = producto_in.model_dump()
        variantes_data = producto_data.pop("variantes")

        nuevo_producto = ProductoModel(**producto_data)
        db.add(nuevo_producto)
        db.flush()
        
        for var_data in variantes_data:
            var_data.pop("id_producto", None)

            if not var_data.get("barcode"):
                var_data["barcode"] = f"P{nuevo_producto.id_producto}-C{var_data['id_color']}-T{var_data['id_talla']}"

            nueva_variante = VarianteModel(
                **var_data,
                id_producto=nuevo_producto.id_producto
            )
            db.add(nueva_variante)
            db.flush()

            if nueva_variante.stock_actual > 0:
                movimiento_inicial = MovimientoModel(
                    id_variante=nueva_variante.id_variante,
                    id_empleado=usuario_actual.id_empleado,
                    cantidad=nueva_variante.stock_actual,
                    tipo_movimiento=TipoMovimientoEnum.ENTRADA,
                    fecha=datetime.now(),
                    motivo="Inventario Inicial (Creación de Producto)",
                    stock_resultante=nueva_variante.stock_actual
                )
                db.add(movimiento_inicial)

        db.commit()
        db.refresh(nuevo_producto)
        return nuevo_producto

    except IntegrityError as e:
        db.rollback()
        msg_error = str(e.orig)
        if "barcode" in msg_error or "Duplicate entry" in msg_error:
            raise HTTPException(status_code=400, detail=f"Error: El código de barras ya existe en otra variante. {msg_error}")
        raise HTTPException(status_code=400, detail=f"Error de integridad de datos: {msg_error}")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# PUT
@endpoint.put("/{id}", response_model=ProductoRead)
def actualizar_producto_info(
    id: int, 
    producto_update: ProductoUpdate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    
    if usuario_actual.funcion.value != "GERENTE":
        raise HTTPException(status_code=403, detail="No tienes permisos para esta función.")

    prod_db = db.query(ProductoModel).filter(ProductoModel.id_producto == id).first()
    if not prod_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = producto_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(prod_db, key, value)

    try:
        db.commit()
        db.refresh(prod_db)
        return prod_db
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# DELETE
@endpoint.delete("/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(
    id_producto: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "GERENTE":
        raise HTTPException(status_code=403, detail="No tienes permisos para esta función.")

    producto = db.query(ProductoModel).filter(ProductoModel.id_producto == id_producto).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    producto.estatus = False
    
    for variante in producto.variantes:
        variante.estatus = False
    try:
        db.commit()
        return {"mensaje": f"El producto {producto.nombre} y sus variantes fueron eliminados correctamente."}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar el producto debido a restricciones de integridad referencial.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))