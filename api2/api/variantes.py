from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.variante import Variante as Variante_model
from schemas.variante import VarianteUpdate, Variante, VarianteUpdate

endpoint = APIRouter(prefix="/variantes", tags=["Variantes"])

def connect_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

@endpoint.get("/", response_model=list[Variante])
def listar_variantes_todos(db: Session = Depends(connect_db)):
    try:
        return db.query(Variante_model).all()
    except Exception as e:
        return {"error": str(e)}

@endpoint.post("/", response_model=Variante)
def crear_variante(variante: VarianteUpdate, db: Session = Depends(connect_db)):
    try:
        nuevo = Variante_model(**variante.model_dump())
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.put("/{id}", response_model=Variante)
def actualizar_variante(id: int, variante: VarianteUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Variante_model).filter(Variante_model.idVariante == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Variante no encontrado")
        for key, value in variante.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.patch("/{id}", response_model=Variante)
def patch_variante(id: int, variante: VarianteUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Variante_model).filter(Variante_model.idVariante == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Variante no encontrado")
        for key, value in variante.model_dump(exclude_unset=True).items():
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
def eliminar_variante(id: int, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Variante_model).filter(Variante_model.idVariante == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Variante no encontrado")
        db.delete(obj)
        db.commit()
        return {"status": "ok", "mensaje": "Variante eliminado"}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}