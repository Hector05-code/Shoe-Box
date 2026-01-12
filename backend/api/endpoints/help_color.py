from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from config_db import sesion_local
from modelos.help_color import Color as ColorModel
from schemas.help_color import ColorCreate, ColorUpdate, ColorRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_usuario_actual 

endpoint = APIRouter(prefix="/colores", tags=["Colores"])

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

# Mock de seguridad (Reemplaza con tu lógica real o importación)
# def get_usuario_actual():
#     class UsuarioMock:
#         id_empleado = 1
#         funcion = "Gerente"
#     return UsuarioMock()

@endpoint.get("/", response_model=List[ColorRead])
def listar_colores(db: Session = Depends(get_db)):
    return db.query(ColorModel).all()

@endpoint.post("/", response_model=ColorRead, status_code=status.HTTP_201_CREATED)
def crear_color(
    color: ColorCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion != "Gerente":
        raise HTTPException(status_code=403, detail="No tienes permisos.")

    nuevo_color = ColorModel(**color.model_dump())
    try:
        db.add(nuevo_color)
        db.commit()
        db.refresh(nuevo_color)
        return nuevo_color
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya existe un color con ese nombre.")

@endpoint.put("/{id}", response_model=ColorRead)
def actualizar_color(
    id: int, 
    color_update: ColorUpdate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion != "Gerente":
        raise HTTPException(status_code=403, detail="Permisos insuficientes.")

    color_db = db.query(ColorModel).filter(ColorModel.id_color == id).first()
    if not color_db:
        raise HTTPException(status_code=404, detail="Color no encontrado")

    for key, value in color_update.model_dump(exclude_unset=True).items():
        setattr(color_db, key, value)

    try:
        db.commit()
        db.refresh(color_db)
        return color_db
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_color(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion != "Gerente":
        raise HTTPException(status_code=403, detail="Permisos insuficientes.")

    color_db = db.query(ColorModel).filter(ColorModel.id_color == id).first()
    if not color_db:
        raise HTTPException(status_code=404, detail="Color no encontrado")

    try:
        db.delete(color_db)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar: Hay variantes de productos usando este color.")