from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from modelos.help_color import Color as ColorModel
from schemas.help_color import ColorCreate, ColorUpdate, ColorRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual 
from utilidades.pin import requerir_permiso_gerente

endpoint = APIRouter(prefix="/colores", tags=["Colores"])

# LEER TODOS
@endpoint.get("/", response_model=List[ColorRead])
def listar_colores(db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    return db.query(ColorModel).all()

# POST
@endpoint.post("/", response_model=ColorRead, status_code=status.HTTP_201_CREATED)
def crear_color(
    color: ColorCreate, 
    db: Session = Depends(get_db),
    _: EmpleadoRead = Depends(get_usuario_actual)
):

    existe = db.query(ColorModel).filter(func.lower(ColorModel.nombre) == color.nombre.lower()).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe un color con ese nombre.")
    nuevo_color = ColorModel(**color.model_dump())
    db.add(nuevo_color)
    db.commit()
    db.refresh(nuevo_color)
    return nuevo_color

# PUT    
@endpoint.put("/{id}", response_model=ColorRead)
def actualizar_color(
    id: int, 
    color_update: ColorUpdate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
    autorizado: bool = Depends(requerir_permiso_gerente)
):

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

# DELETE
@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_color(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
    autorizado: bool = Depends(requerir_permiso_gerente)
):

    color_db = db.query(ColorModel).filter(ColorModel.id_color == id).first()
    if not color_db:
        raise HTTPException(status_code=404, detail="Color no encontrado")

    try:
        db.delete(color_db)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar: Hay variantes de productos usando este color.")