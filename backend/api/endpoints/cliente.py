from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from config_db import sesion_local
from modelos.cliente import Cliente as ClienteModel
from schemas.cliente import ClienteCreate, ClienteUpdate, ClienteRead
from schemas.empleado import EmpleadoRead
from utilidades.login import get_usuario_actual
endpoint = APIRouter(prefix="/clientes", tags=["Clientes"])

# def get_usuario_actual(token: str = "token_falso"): 
#     # Aquí iría la lógica de decodificar el token JWT
#     # Por ahora, simulamos que es un objeto con el rol del usuario
#     class UsuarioSimulado:
#         id_empleado = 1
#         funcion = "Gerente" # O "Gerente"
    
    # return UsuarioSimulado()
def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

# --- LEER TODOS (GET) ---
@endpoint.get("/", response_model=List[ClienteRead])
def listar_clientes(db: Session = Depends(get_db), usuario_actual: EmpleadoRead = Depends(get_usuario_actual)):
    # No hace falta try/except aquí a menos que la DB esté caída.
    # FastAPI maneja los errores 500 automáticamente.
    return db.query(ClienteModel).all()

# --- LEER UNO (GET) ---
@endpoint.get("/{id}", response_model=ClienteRead)
def obtener_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(ClienteModel).filter(ClienteModel.id_cliente_ci == id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

# --- CREAR (POST) ---
@endpoint.post("/", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    try:
        # Convertimos el esquema Pydantic a Modelo SQLAlchemy
        # model_dump() reemplaza a dict() en Pydantic v2
        nuevo_cliente = ClienteModel(**cliente.model_dump())
        
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        return nuevo_cliente
        
    except IntegrityError:
        db.rollback()
        # Esto ocurre si intentan registrar una Cédula que ya existe
        raise HTTPException(status_code=400, detail="El cliente con esa Cédula ya existe.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- ACTUALIZAR (PUT) ---
# PUT se usa generalmente para reemplazar todo el objeto, pero aquí actuará flexible
@endpoint.put("/{id}", response_model=ClienteRead)
def actualizar_cliente(id: int, cliente_data: ClienteUpdate, db: Session = Depends(get_db)):
    # 1. Buscar
    cliente_db = db.query(ClienteModel).filter(ClienteModel.id_cliente_ci == id).first()
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    # 2. Preparar datos (excluyendo nulos para no borrar datos que no enviaste)
    update_data = cliente_data.model_dump(exclude_unset=True)

    # 3. Actualizar campos
    for key, value in update_data.items():
        setattr(cliente_db, key, value)

    # 4. Guardar
    try:
        db.commit()
        db.refresh(cliente_db)
        return cliente_db
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- ELIMINAR (DELETE) ---
@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cliente(id: int, db: Session = Depends(get_db), usuario_actual: EmpleadoRead = Depends(get_usuario_actual)):
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para esta función.")
    cliente_db = db.query(ClienteModel).filter(ClienteModel.id_cliente_ci == id).first()
    if not cliente_db:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    try:
        db.delete(cliente_db)
        db.commit()
        # En 204 No Content, no se retorna nada (ni JSON)
        return 
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al eliminar: {str(e)}")