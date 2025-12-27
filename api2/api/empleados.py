from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.empleado import Empleado as Empleado_model
from schemas.empleado import EmpleadoCreate, Empleado, EmpleadoUpdate

endpoint = APIRouter(prefix="/empleados", tags=["Empleados"])

def connect_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

@endpoint.get("/", response_model=list[Empleado])
def listar_Empleados_todos(db: Session = Depends(connect_db)):
    try:
        return db.query(Empleado_model).all()
    except Exception as e:
        return {"error": str(e)}

@endpoint.post("/", response_model=Empleado)
def crear_Empleado(empleado: EmpleadoCreate, db: Session = Depends(connect_db)):
    try:
        nuevo = Empleado_model(**empleado.model_dump())
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.put("/{id}", response_model=Empleado)
def actualizar_Empleado(id: int, empleado: EmpleadoUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Empleado_model).filter(Empleado_model.id_Empleado == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        for key, value in empleado.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.patch("/{id}", response_model=Empleado)
def patch_Empleado(id: int, empleado: EmpleadoUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Empleado_model).filter(Empleado_model.id_Empleado == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        for key, value in empleado.model_dump(exclude_unset=True).items():
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
def eliminar_Empleado(id: int, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Empleado_model).filter(Empleado_model.id_Empleado == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")
        db.delete(obj)
        db.commit()
        return {"status": "ok", "mensaje": "Empleado eliminado"}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}