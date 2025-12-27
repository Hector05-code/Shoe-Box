from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.movimiento import Movimiento as Movimiento_model
from schemas.movimiento import MovimientoCreate, Movimiento, MovimientoUpdate

endpoint = APIRouter(prefix="/movimientos", tags=["Movimientos"])

def connect_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

@endpoint.get("/", response_model=list[Movimiento])
def listar_movimientos_todos(db: Session = Depends(connect_db)):
    try:
        return db.query(Movimiento_model).all()
    except Exception as e:
        return {"error": str(e)}

@endpoint.post("/", response_model=Movimiento)
def crear_movimiento(movimiento: MovimientoCreate, db: Session = Depends(connect_db)):
    try:
        nuevo = Movimiento_model(**movimiento.model_dump())
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.put("/{id}", response_model=Movimiento)
def actualizar_movimiento(id: int, movimiento: MovimientoUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Movimiento_model).filter(Movimiento_model.id_Movimiento == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        for key, value in movimiento.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.patch("/{id}", response_model=Movimiento)
def patch_movimiento(id: int, movimiento: MovimientoUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Movimiento_model).filter(Movimiento_model.id_Movimiento == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        for key, value in movimiento.model_dump(exclude_unset=True).items():
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
def eliminar_movimiento(id: int, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Movimiento_model).filter(Movimiento_model.id_Movimiento == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")
        db.delete(obj)
        db.commit()
        return {"status": "ok", "mensaje": "Movimiento eliminado"}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}