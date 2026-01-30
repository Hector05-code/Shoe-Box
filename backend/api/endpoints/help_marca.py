from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from modelos.help_marca import Marca as MarcaModel
from schemas.help_marca import MarcaCreate, MarcaRead, MarcaUpdate
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual

endpoint = APIRouter(prefix="/marcas", tags=["Marcas"])

# LEER TODOS
@endpoint.get("/", response_model=List[MarcaRead])
def listar_marcas(db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    return db.query(MarcaModel).filter(MarcaModel.estatus == True).all()

#POST
@endpoint.post("/", response_model=MarcaRead, status_code=status.HTTP_201_CREATED)
def crear_marca(
    marca_in: MarcaCreate, 
    db: Session = Depends(get_db),
    _: EmpleadoRead = Depends(get_usuario_actual)
):
    existe = db.query(MarcaModel).filter(func.lower(MarcaModel.nombre) == marca_in.nombre.lower()).first()
    if existe:
        raise HTTPException(status_code=400, detail=f"La marca '{marca_in.nombre}' ya existe.")

    nueva_marca = MarcaModel(nombre=marca_in.nombre)
    db.add(nueva_marca)
    db.commit()
    db.refresh(nueva_marca)
    return nueva_marca
# PUT
@endpoint.put("/{id}", response_model=MarcaRead)
def editar_marca(
    id: int, 
    marca_in: MarcaUpdate, 
    db: Session = Depends(get_db),
    usuario: EmpleadoRead = Depends(get_usuario_actual)
):
    if usuario.funcion.value != "GERENTE": # Asegúrate de usar mayúsculas aquí también
        raise HTTPException(status_code=403, detail="Permisos insuficientes.")

    marca = db.query(MarcaModel).get(id)
    if not marca:
        raise HTTPException(status_code=404, detail="Marca no encontrada")

    if marca_in.nombre:
        marca.nombre = marca_in.nombre
    if marca_in.estatus is not None:
        marca.estatus = marca_in.estatus

    db.commit()
    db.refresh(marca)
    return marca