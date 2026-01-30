from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from modelos.cliente import Cliente as ClienteModel
from schemas.cliente import ClienteCreate, ClienteUpdate, ClienteRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_db, get_usuario_actual

endpoint = APIRouter(prefix="/clientes", tags=["Clientes"])

# LEER TODOS
@endpoint.get("/", response_model=List[ClienteRead])
def listar_clientes(db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual), mostrar_inactivos: bool = False):
    clientes = db.query(ClienteModel)
    if not mostrar_inactivos:
        clientes = clientes.filter(ClienteModel.estatus == True)
    return clientes.all()

# LEER UNO
@endpoint.get("/{id}", response_model=ClienteRead)
def obtener_cliente(id: int, db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    cliente = db.query(ClienteModel).filter(ClienteModel.id_cliente_ci == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

# POST
@endpoint.post("/", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    try:
        nuevo_cliente = ClienteModel(**cliente.model_dump())
        
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        return nuevo_cliente
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El cliente con esa Cédula ya existe.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# PUT
@endpoint.put("/{id}", response_model=ClienteRead)
def actualizar_cliente(id: int, cliente_data: ClienteUpdate, db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    cliente_db = db.query(ClienteModel).filter(ClienteModel.id_cliente_ci == id).first()
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    update_data = cliente_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(cliente_db, key, value)
    try:
        db.commit()
        db.refresh(cliente_db)
        return cliente_db
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ELIMINAR
@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(id: int, db: Session = Depends(get_db), usuario_actual: EmpleadoRead = Depends(get_usuario_actual)):
    if usuario_actual.funcion.value != "GERENTE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para esta función.")
    cliente_db = db.query(ClienteModel).filter(ClienteModel.id_cliente_ci == id).first()
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    try:
        db.delete(cliente_db)
        db.commit()

    except IntegrityError:
        db.rollback()
        cliente_db.estatus = False
        db.add(cliente_db)
        db.commit()
        return
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")