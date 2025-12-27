from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.cliente import Cliente as Cliente_model
from schemas.cliente import ClienteCreate, Cliente, ClienteUpdate

endpoint = APIRouter(prefix="/clientes", tags=["Clientes"])

def connect_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

@endpoint.get("/", response_model=list[Cliente])
def listar_clientes(db: Session = Depends(connect_db)):
    try:
        return db.query(Cliente_model).all()
    except Exception as e:
        return {"error": str(e)}

@endpoint.post("/", response_model=Cliente)
def crear_cliente(cliente: ClienteCreate, db: Session = Depends(connect_db)):
    try:
        nuevo = Cliente_model(**Cliente.model_dump())
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.put("/{id}", response_model=Cliente)
def actualizar_Cliente(id: int, Cliente: ClienteUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Cliente_model).filter(Cliente_model.id_Cliente_CI == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        for key, value in Cliente.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.patch("/{id}", response_model=Cliente)
def patch_Cliente(id: int, Cliente: ClienteUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Cliente_model).filter(Cliente_model.id_Cliente_CI == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        for key, value in Cliente.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.delete("/{id}")
def eliminar_Cliente(id: int, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Cliente_model).filter(Cliente_model.id_Cliente_CI == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        db.delete(obj)
        db.commit()
        return {"status": "ok", "mensaje": "Cliente eliminado"}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}