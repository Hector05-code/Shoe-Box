from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from modelos.help_talla import Talla as TallaModel
from schemas.help_talla import TallaCreate, TallaUpdate, TallaRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual 

endpoint = APIRouter(prefix="/tallas", tags=["Tallas"])

# LEER TODOS
@endpoint.get("/", response_model=List[TallaRead])
def listar_tallas(db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    return db.query(TallaModel).order_by(TallaModel.id_talla).all()

# POST
@endpoint.post("/", response_model=TallaRead, status_code=status.HTTP_201_CREATED)
def crear_talla(
    talla: TallaCreate, 
    db: Session = Depends(get_db),
    _: EmpleadoRead = Depends(get_usuario_actual)
):
    existe = db.query(TallaModel).filter(func.lower(TallaModel.nombre) == talla.nombre.lower()).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe una talla con ese nombre.")
    
    nueva_talla = TallaModel(**talla.model_dump())
    db.add(nueva_talla)
    db.commit()
    db.refresh(nueva_talla)
    return nueva_talla

# PUT
@endpoint.put("/{id}", response_model=TallaRead)
def actualizar_talla(
    id: int, 
    talla_update: TallaUpdate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "GERENTE":
        raise HTTPException(status_code=403, detail="No tienes permisos para esta función.")

    talla_db = db.query(TallaModel).filter(TallaModel.id_talla == id).first()
    if not talla_db:
        raise HTTPException(status_code=404, detail="Talla no encontrada")

    for key, value in talla_update.model_dump(exclude_unset=True).items():
        setattr(talla_db, key, value)

    try:
        db.commit()
        db.refresh(talla_db)
        return talla_db
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

#DELETE
@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_talla(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "GERENTE":
        raise HTTPException(status_code=403, detail="No tienes permisos para esta función.")

    talla_db = db.query(TallaModel).filter(TallaModel.id_talla == id).first()
    if not talla_db:
        raise HTTPException(status_code=404, detail="Talla no encontrada")

    try:
        db.delete(talla_db)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar: Hay productos usando esta talla.")