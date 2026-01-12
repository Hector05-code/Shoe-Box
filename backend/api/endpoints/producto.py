from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List

# Imports locales
from config_db import sesion_local
# Modelos DB
from modelos.producto import Producto as ProductoModel
from modelos.variante import Variante as VarianteModel
from modelos.movimiento import Movimiento as MovimientoModel, TipoMovimientoEnum
# Schemas
from schemas.producto import ProductoCreate, ProductoUpdate, ProductoRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_usuario_actual

endpoint = APIRouter(prefix="/productos", tags=["Productos"])

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

# Mock de seguridad (mismo que usamos antes)
# def get_usuario_actual():
#     class UsuarioMock:
#         id_empleado = 1
#         funcion = "Gerente" 
#     return UsuarioMock()

# ==========================================
# RUTAS DE LECTURA (Optimizado)
# ==========================================

@endpoint.get("/", response_model=List[ProductoRead])
def listar_productos(db: Session = Depends(get_db), mostrar_inactivos: bool = False):
    # OPTIMIZACIÓN CRÍTICA: 'joinedload'
    # Esto le dice a SQL: "Traeme el producto Y SUS variantes Y SU categoría en UNA sola consulta"
    # Sin esto, tu API sería extremadamente lenta.
    if not mostrar_inactivos:
        productos = db.query(ProductoModel).options(
            joinedload(ProductoModel.variantes).joinedload(VarianteModel.color_rel),
            joinedload(ProductoModel.variantes).joinedload(VarianteModel.talla_rel),
            joinedload(ProductoModel.categoria)
        ).filter(ProductoModel.estatus).all()
    return productos

@endpoint.get("/{id}", response_model=ProductoRead)
def obtener_producto(id: int, db: Session = Depends(get_db)):
    producto = db.query(ProductoModel).options(
        joinedload(ProductoModel.variantes).joinedload(VarianteModel.color_rel),
        joinedload(ProductoModel.variantes).joinedload(VarianteModel.talla_rel),
        joinedload(ProductoModel.categoria)
    ).filter(ProductoModel.id_producto == id).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# ==========================================
# RUTAS DE ESCRITURA (Transacción Compleja)
# ==========================================

@endpoint.post("/", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def crear_producto_completo(
    producto_in: ProductoCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    # 1. Permisos
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Solo Gerentes pueden registrar productos.")

    try:
        # 2. Separar datos del Padre y de los Hijos
        # model_dump() convierte el Pydantic a diccionario
        producto_data = producto_in.model_dump()
        
        # Sacamos la lista de variantes del diccionario (pop) porque
        # el modelo ProductoModel no tiene una columna "variantes", tiene una relación.
        variantes_data = producto_data.pop("variantes")

        # 3. Crear el PADRE (Producto)
        nuevo_producto = ProductoModel(**producto_data)
        db.add(nuevo_producto)
        
        # FLUSH: Enviamos los datos a la DB para que nos asigne un ID, 
        # pero NO confirmamos (commit) todavía.
        db.flush() 
        
        # Ahora nuevo_producto.id_producto ya tiene un número (ej: 55)

        # 4. Crear los HIJOS (Variantes)
        for var_data in variantes_data:
            # Creamos la variante vinculándola al ID del padre recién creado
            nueva_variante = VarianteModel(
                **var_data,
                id_producto=nuevo_producto.id_producto 
            )
            db.add(nueva_variante)
            db.flush() # Obtenemos ID de la variante para el movimiento

            # 5. BONUS: Registro Automático de Stock Inicial
            # Si declaraste stock inicial, creamos el Movimiento automáticamente
            if nueva_variante.stock_actual > 0:
                movimiento_inicial = MovimientoModel(
                    id_variante=nueva_variante.id_variante,
                    id_empleado=usuario_actual.id_empleado,
                    cantidad=nueva_variante.stock_actual,
                    tipo_movimiento=TipoMovimientoEnum.entrada, # O "INVENTARIO_INICIAL"
                    fecha=None
                )
                db.add(movimiento_inicial)

        # 6. Si todo salió bien, guardamos definitivamente
        db.commit()
        
        # 7. Refrescamos para devolver el objeto completo con relaciones cargadas
        db.refresh(nuevo_producto)
        return nuevo_producto

    except IntegrityError as e:
        db.rollback()
        # Error común: SKU duplicado o Nombre duplicado
        raise HTTPException(status_code=400, detail=f"Error de integridad (posible SKU o Nombre duplicado): {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@endpoint.put("/{id}", response_model=ProductoRead)
def actualizar_producto_info(
    id: int, 
    producto_update: ProductoUpdate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    # """
    # Actualiza solo la información base del producto (Nombre, Precio, Marca).
    # NO actualiza variantes aquí (eso debe tener su propio endpoint).
    # """
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Requiere permisos de Gerente.")

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


# endpoints/producto.py

@endpoint.delete("/{id_producto}", status_code=status.HTTP_204_NO_CONTENT)
def desactivar_producto(
    id_producto: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Solo Gerentes pueden registrar productos.")
    # """
    # BAJA LÓGICA: No borra el registro, solo lo marca como inactivo.
    # Mantiene el historial de ventas intacto.
    # """
    producto = db.query(ProductoModel).filter(ProductoModel.id_producto == id_producto).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Simplemente cambiamos el estado
    producto.estatus = False 
    db.add(producto)
    db.commit()
    
    return None

@endpoint.delete("/{id_producto}/forzar", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto_permanentemente(
    id_producto: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    # """
    # BAJA FÍSICA: Borra el registro de la BD.
    # SOLO funciona si el producto NO tiene movimientos ni ventas.
    # """
    # 1. Seguridad extra: Solo Gerentes deberían poder hacer esto
    
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Solo Gerentes pueden registrar productos.")

    producto = db.query(ProductoModel).filter(ProductoModel.id_producto == id_producto).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    try:
        # Intentamos borrar de verdad
        db.delete(producto)
        db.commit()
        return None

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Este producto tiene historial (ventas o compras). Usa el borrado normal para desactivarlo."
        )

# @endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def eliminar_producto(
#     id: int, 
#     db: Session = Depends(get_db),
#     usuario_actual = Depends(get_usuario_actual)
# ):
#     if usuario_actual.funcion != "Gerente":
#         raise HTTPException(status_code=403, detail="Requiere permisos de Gerente.")

#     # Al borrar el Padre, SQLAlchemy borrará los hijos si configuraste
#     # cascade="all, delete-orphan" en el modelo.
#     prod_db = db.query(ProductoModel).filter(ProductoModel.id_producto == id).first()
    
#     if not prod_db:
#         raise HTTPException(status_code=404, detail="Producto no encontrado")

#     try:
#         db.delete(prod_db)
#         db.commit()
#         return
#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(status_code=400, detail="No se puede eliminar: El producto tiene movimientos asociados.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))