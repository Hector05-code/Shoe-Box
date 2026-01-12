from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List

# Configuración y DB
from config_db import sesion_local
from modelos.variante import Variante as VarianteModel
from modelos.producto import Producto as ProductoModel
from modelos.movimiento import Movimiento as MovimientoModel, TipoMovimientoEnum

# Schemas
# Importamos VarianteCreateSuelta porque aquí SI necesitamos el ID del padre
from schemas.variante import VarianteRead, VarianteUpdate, VarianteCreateSuelta 
from schemas.empleado import EmpleadoRead
from utilidades.login import get_usuario_actual
endpoint = APIRouter(prefix="/variantes", tags=["Variantes (Inventario)"])

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

# Mock de seguridad
# def get_usuario_actual():
#     class UsuarioMock:
#         id_empleado = 1
#         funcion = "Gerente" 
#     return UsuarioMock()

# ==========================================
# RUTAS DE LECTURA
# ==========================================

@endpoint.get("/", response_model=List[VarianteRead])
def listar_variantes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    # """
    # Lista todas las variantes existentes. 
    # Usamos joinedload para traer Color y Talla en la misma consulta (Optimización).
    # """
    variantes = db.query(VarianteModel).options(
        joinedload(VarianteModel.color_rel),
        joinedload(VarianteModel.talla_rel),
        # Opcional: Si quieres ver el nombre del producto padre también
        joinedload(VarianteModel.producto_rel) 
    ).offset(skip).limit(limit).all()
    
    return variantes

@endpoint.get("/{id}", response_model=VarianteRead)
def obtener_variante(id: int, db: Session = Depends(get_db)):
    variante = db.query(VarianteModel).options(
        joinedload(VarianteModel.color_rel),
        joinedload(VarianteModel.talla_rel)
    ).filter(VarianteModel.id_variante == id).first()
    
    if not variante:
        raise HTTPException(status_code=404, detail="Variante no encontrada")
    return variante

# ==========================================
# RUTAS DE ESCRITURA (Solo Gerentes)
# ==========================================

@endpoint.post("/", response_model=VarianteRead, status_code=status.HTTP_201_CREATED)
def agregar_variante_a_producto(
    variante_in: VarianteCreateSuelta, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    # """
    # Agrega una variante suelta (ej: Nueva Talla) a un producto que YA existe.
    # """
    if usuario_actual.funcion != "Gerente":
        raise HTTPException(status_code=403, detail="Requiere permisos de Gerente.")

    # 1. Validar que el producto padre exista
    producto_padre = db.query(ProductoModel).filter(ProductoModel.id_producto == variante_in.id_producto).first()
    if not producto_padre:
        raise HTTPException(status_code=404, detail=f"El producto padre con ID {variante_in.id_producto} no existe.")

    existe_barcode = db.query(VarianteModel).filter(VarianteModel.barcode == variante_in.barcode).first()
    if existe_barcode:
        raise HTTPException(
            status_code=400, 
            detail=f"El código de barras '{variante_in.barcode}' ya está registrado en el producto '{existe_barcode.producto_rel.nombre}'."
        )

    try:
        # 2. Crear la variante
        nueva_variante = VarianteModel(**variante_in.model_dump())
        db.add(nueva_variante)
        db.flush() # Generar ID

        # 3. Registrar Movimiento Inicial (Si hay stock)
        # Esto mantiene la coherencia del Kardex
        if nueva_variante.stock_actual > 0:
            movimiento = MovimientoModel(
                id_variante=nueva_variante.id_variante,
                id_empleado=usuario_actual.id_empleado,
                cantidad=nueva_variante.stock_actual,
                tipo_movimiento=TipoMovimientoEnum.entrada, # O "AJUSTE_POSITIVO"
                referencia="Ingreso de nueva variante al catálogo"
            )
            db.add(movimiento)

        db.commit()
        db.refresh(nueva_variante)
        return nueva_variante

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error: El SKU ya existe o combinación inválida.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@endpoint.put("/{id}", response_model=VarianteRead)
def actualizar_variante(
    id: int, 
    variante_update: VarianteUpdate, 
    db: Session = Depends(get_db),
    usuario_actual : EmpleadoRead = Depends(get_usuario_actual)
):
    # """
    # Actualiza SKU, Color, Talla o Stock.
    # NOTA: Si se cambia el stock aquí, se generará un movimiento de AJUSTE automáticamente.
    # """
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Requiere permisos de Gerente.")

    variante_db = db.query(VarianteModel).filter(VarianteModel.id_variante == id).first()
    if not variante_db:
        raise HTTPException(status_code=404, detail="Variante no encontrada")

    datos_nuevos = variante_update.model_dump(exclude_unset=True)

    # Lógica especial para cambios de Stock manuales (Correcciones)
    stock_nuevo = datos_nuevos.get("stock_actual")
    
    if stock_nuevo is not None and stock_nuevo != variante_db.stock_actual:
        # Calculamos la diferencia
        diferencia = stock_nuevo - variante_db.stock_actual
        tipo = TipoMovimientoEnum.ajuste if diferencia > 0 else TipoMovimientoEnum.ajuste
        
        # Registramos por qué cambió el stock (Auditoría)
        movimiento_ajuste = MovimientoModel(
            id_variante=id,
            id_empleado=usuario_actual.id_empleado,
            cantidad=abs(diferencia), # Siempre positivo en la columna cantidad
            tipo_movimiento=tipo,
            referencia="Corrección manual de stock desde panel"
        )
        db.add(movimiento_ajuste)

    # Aplicar cambios
    for key, value in datos_nuevos.items():
        setattr(variante_db, key, value)

    try:
        db.commit()
        db.refresh(variante_db)
        return variante_db
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad (posible SKU duplicado).")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_variante(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    # """
    # Elimina una variante específica (ej: Ya no vendemos Talla XS).
    # """
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Requiere permisos de Gerente.")

    variante_db = db.query(VarianteModel).filter(VarianteModel.id_variante == id).first()
    
    if not variante_db:
        raise HTTPException(status_code=404, detail="Variante no encontrada")

    try:
        db.delete(variante_db)
        db.commit()
        return
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar: Esta variante ya tiene ventas o movimientos asociados.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))