from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from modelos.help_categoria import Categoria as CategoriaModel
from schemas.help_categoria import CategoriaCreate, CategoriaUpdate, CategoriaRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual
from utilidades.pin import requerir_permiso_gerente 

endpoint = APIRouter(prefix="/categorias", tags=["Categorías"])

# LEER TODOS
@endpoint.get("/", response_model=List[CategoriaRead])
def listar_categorias(db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    return db.query(CategoriaModel).all()

# POST
@endpoint.post("/", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    categoria: CategoriaCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
    autorizado: bool = Depends(requerir_permiso_gerente)
):

    existe = db.query(CategoriaModel).filter(
        func.lower(CategoriaModel.nombre) == categoria.nombre.lower()).first()
    if existe:
        raise HTTPException(status_code=400, detail="Esta categoría ya existe")
    
    nueva_cat = CategoriaModel(**categoria.model_dump())
    try:
        db.add(nueva_cat)
        db.commit()
        db.refresh(nueva_cat)
        return nueva_cat
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre.")

# PUT
@endpoint.put("/{id}", response_model=CategoriaRead)
def actualizar_categoria(
    id: int, 
    cat_update: CategoriaUpdate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
    autorizado: bool = Depends(requerir_permiso_gerente)
):

    cat_db = db.query(CategoriaModel).filter(CategoriaModel.id_categoria == id).first()
    if not cat_db:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    for key, value in cat_update.model_dump(exclude_unset=True).items():
        setattr(cat_db, key, value)

    try:
        db.commit()
        db.refresh(cat_db)
        return cat_db
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El nombre ya está en uso.")

# DELETE
@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
    autorizado: bool = Depends(requerir_permiso_gerente)
):

    cat_db = db.query(CategoriaModel).filter(CategoriaModel.id_categoria == id).first()
    if not cat_db:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    try:
        db.delete(cat_db)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar: Hay productos asociados a esta categoría.")