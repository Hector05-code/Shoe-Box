from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.detalle_venta import Detalle_venta as Detalle_venta_model
from schemas.detalle_venta import Detalle_ventaCreate, Detalle_venta, Detalle_ventaUpdate

endpoint = APIRouter(prefix="/detalle_ventas", tags=["Detalle_ventas"])

def connect_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

@endpoint.get("/", response_model=list[Detalle_venta])
def listar_detalle_ventas_todos(db: Session = Depends(connect_db)):
    try:
        return db.query(Detalle_venta_model).all()
    except Exception as e:
        return {"error": str(e)}

@endpoint.post("/", response_model=Detalle_venta)
def crear_detalle_venta(detalle_venta: Detalle_ventaCreate, db: Session = Depends(connect_db)):
    try:
        nuevo = Detalle_venta_model(**detalle_venta.model_dump())
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.put("/{id}", response_model=Detalle_venta)
def actualizar_detalle_venta(id: int, detalle_venta: Detalle_ventaUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Detalle_venta_model).filter(Detalle_venta_model.id_Detalle_Venta == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Detalle_venta no encontrado")
        for key, value in detalle_venta.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.patch("/{id}", response_model=Detalle_venta)
def patch_detalle_venta(id: int, detalle_venta: Detalle_ventaUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Detalle_venta_model).filter(Detalle_venta_model.id_Detalle_Venta == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Detalle_venta no encontrado")
        for key, value in detalle_venta.model_dump(exclude_unset=True).items():
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
def eliminar_detalle_venta(id: int, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Detalle_venta_model).filter(Detalle_venta_model.id_Detalle_venta == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Detalle_venta no encontrado")
        db.delete(obj)
        db.commit()
        return {"status": "ok", "mensaje": "Detalle_venta eliminado"}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}