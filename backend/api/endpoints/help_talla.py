from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from config_db import sesion_local
from modelos.help_talla import Talla as TallaModel
from schemas.help_talla import TallaCreate, TallaUpdate, TallaRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_usuario_actual 

endpoint = APIRouter(prefix="/tallas", tags=["Tallas"])

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

@endpoint.get("/", response_model=List[TallaRead])
def listar_tallas(db: Session = Depends(get_db)):
    # Tip: Podrías ordenarlas por ID para que salgan S, M, L y no alfabéticamente L, M, S
    return db.query(TallaModel).order_by(TallaModel.id_talla).all()

@endpoint.post("/", response_model=TallaRead, status_code=status.HTTP_201_CREATED)
def crear_talla(
    talla: TallaCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Permisos insuficientes.")

    nueva_talla = TallaModel(**talla.model_dump())
    try:
        db.add(nueva_talla)
        db.commit()
        db.refresh(nueva_talla)
        return nueva_talla
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="La talla ya existe.")

@endpoint.put("/{id}", response_model=TallaRead)
def actualizar_talla(
    id: int, 
    talla_update: TallaUpdate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Permisos insuficientes.")

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

@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_talla(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Permisos insuficientes.")

    talla_db = db.query(TallaModel).filter(TallaModel.id_talla == id).first()
    if not talla_db:
        raise HTTPException(status_code=404, detail="Talla no encontrada")

    try:
        db.delete(talla_db)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="No se puede eliminar: Hay productos usando esta talla.")