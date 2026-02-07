from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from passlib.context import CryptContext
from utilidades.login import get_db, get_usuario_actual
from utilidades.cripto import get_password_hash, get_pin_hash
from modelos.empleado import Empleado as EmpleadoModel
from schemas.empleado import EmpleadoCreate, EmpleadoUpdate, EmpleadoRead
from utilidades.pin import requerir_permiso_gerente

endpoint = APIRouter(prefix="/empleados", tags=["Empleados"])

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# LEER TODOS
@endpoint.get("/", response_model=List[EmpleadoRead])
def listar_empleados(db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual), mostrar_inactivos: bool = False):
    empleados = db.query(EmpleadoModel)
    if not mostrar_inactivos:
        empleados = empleados.filter(EmpleadoModel.estatus == True)
    return empleados.all()

# LEER UNO
@endpoint.get("/{id}", response_model=EmpleadoRead)
def obtener_empleado(id: int, db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    empleado = db.query(EmpleadoModel).filter(EmpleadoModel.id_empleado == id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

# POST
@endpoint.post("/", response_model=EmpleadoRead, status_code=status.HTTP_201_CREATED)
def crear_empleado(
    empleado: EmpleadoCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
    autorizado: bool = Depends(requerir_permiso_gerente)
):

    empleado_existente = db.query(EmpleadoModel).filter(
        func.lower(EmpleadoModel.usuario) == empleado.usuario.lower()
    ).first()

    if empleado_existente:
        raise HTTPException(
            status_code=400, 
            detail=f"El usuario '{empleado.usuario}' ya está registrado."
        )

    try:
        hashed_password = get_password_hash(empleado.contrasena)
        
        hashed_pin = None
        if empleado.pin_autorizacion:
            hashed_pin = get_pin_hash(empleado.pin_autorizacion)
        
        nuevo_empleado = EmpleadoModel(
            id_empleado=empleado.id_empleado,
            nombre=empleado.nombre,
            apellido=empleado.apellido,
            telefono=empleado.telefono,
            direccion=empleado.direccion,
            usuario=empleado.usuario,
            contrasena=hashed_password,
            funcion=empleado.funcion.value,
            pin_autorizacion=hashed_pin,
            estatus=True
        )
        
        db.add(nuevo_empleado)
        db.commit()
        db.refresh(nuevo_empleado)
        return nuevo_empleado

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"El Usuario ya existe. {str(e)}")
        
    except Exception as e:
        db.rollback()
        print(f"Error general: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# PUT
@endpoint.put("/{id}", response_model=EmpleadoRead)
def actualizar_empleado(
    id: int, 
    datos_entrada: EmpleadoUpdate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
    autorizado: bool = Depends(requerir_permiso_gerente)
):

    empleado_db = db.query(EmpleadoModel).filter(EmpleadoModel.id_empleado == id).first()
    if not empleado_db:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    update_data = datos_entrada.model_dump(exclude_unset=True)

    if "contrasena" in update_data:
        update_data["contrasena"] = pwd_context.hash(update_data["contrasena"])

    for key, value in update_data.items():
        setattr(empleado_db, key, value)

    try:
        db.commit()
        db.refresh(empleado_db)
        return empleado_db
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El nombre de Usuario / C.I. ya está ocupado.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# DELETE
@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_empleado(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
    autorizado: bool = Depends(requerir_permiso_gerente)
):

    empleado_db = db.query(EmpleadoModel).filter(EmpleadoModel.id_empleado == id).first()
    if not empleado_db:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    if empleado_db.id_empleado == usuario_actual.id_empleado:
         raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario.")

    try:
        db.delete(empleado_db)
        db.commit()
        return
    except IntegrityError:
        db.rollback()
        empleado_db.estatus = False
        db.add(empleado_db)
        db.commit()
        return
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")