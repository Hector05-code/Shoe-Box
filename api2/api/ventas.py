from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.venta import Venta as Venta_model
from schemas.venta import VentaCreate, Venta, VentaUpdate

endpoint = APIRouter(prefix="/ventas", tags=["Ventas"])

def connect_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

@endpoint.get("/", response_model=list[Venta])
def listar_ventas_todos(db: Session = Depends(connect_db)):
    try:
        return db.query(Venta_model).all()
    except Exception as e:
        return {"error": str(e)}

@endpoint.post("/", response_model=Venta)
def crear_venta(venta: VentaCreate, db: Session = Depends(connect_db)):
    try:
        nuevo = Venta_model(**venta.model_dump())
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.put("/{id}", response_model=Venta)
def actualizar_venta(id: int, venta: VentaUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Venta_model).filter(Venta_model.id_venta == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Venta no encontrado")
        for key, value in venta.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.patch("/{id}", response_model=Venta)
def patch_venta(id: int, venta: VentaUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Venta_model).filter(Venta_model.id_venta == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Venta no encontrado")
        for key, value in venta.model_dump(exclude_unset=True).items():
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
def eliminar_venta(id: int, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Venta_model).filter(Venta_model.id_venta == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Venta no encontrado")
        db.delete(obj)
        db.commit()
        return {"status": "ok", "mensaje": "Venta eliminado"}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}