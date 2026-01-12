from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from config_db import sesion_local
# Importamos Modelo y Schemas
from modelos.help_categoria import Categoria as CategoriaModel
from schemas.help_categoria import CategoriaCreate, CategoriaUpdate, CategoriaRead
# Importamos Schemas de Empleado para permisos
from schemas.empleado import EmpleadoRead
from utilidades.login import get_usuario_actual 

endpoint = APIRouter(prefix="/categorias", tags=["Categorías"])

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

# --- CRUD ---

@endpoint.get("/", response_model=List[CategoriaRead])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(CategoriaModel).all()

@endpoint.post("/", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def crear_categoria(
    categoria: CategoriaCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="No tienes permisos.")

    nueva_cat = CategoriaModel(**categoria.model_dump())
    try:
        db.add(nueva_cat)
        db.commit()
        db.refresh(nueva_cat)
        return nueva_cat
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre.")

@endpoint.put("/{id}", response_model=CategoriaRead)
def actualizar_categoria(
    id: int, 
    cat_update: CategoriaUpdate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Permisos insuficientes.")

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

@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Permisos insuficientes.")

    cat_db = db.query(CategoriaModel).filter(CategoriaModel.id_categoria == id).first()
    if not cat_db:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    try:
        db.delete(cat_db)
        db.commit()
    except IntegrityError:
        db.rollback()
        # Esto pasa si intentas borrar "Camisas" y hay productos asociados a ella
        raise HTTPException(status_code=400, detail="No se puede eliminar: Hay productos asociados a esta categoría.")