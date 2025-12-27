from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.producto import Producto as Producto_model
from schemas.producto import ProductoCreate, Producto, ProductoUpdate

endpoint = APIRouter(prefix="/productos", tags=["Productos"])

def connect_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

@endpoint.get("/", response_model=list[Producto])
def listar_productos_todos(db: Session = Depends(connect_db)):
    try:
        return db.query(Producto_model).all()
    except Exception as e:
        return {"error": str(e)}

@endpoint.post("/", response_model=Producto)
def crear_producto(producto: ProductoCreate, db: Session = Depends(connect_db)):
    try:
        nuevo = Producto_model(**producto.model_dump())
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.put("/{id}", response_model=Producto)
def actualizar_producto(id: int, producto: ProductoUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Producto_model).filter(Producto_model.id_producto == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        for key, value in producto.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}

@endpoint.patch("/{id}", response_model=Producto)
def patch_producto(id: int, producto: ProductoUpdate, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Producto_model).filter(Producto_model.id_producto == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        for key, value in producto.model_dump(exclude_unset=True).items():
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
def eliminar_producto(id: int, db: Session = Depends(connect_db)):
    try:
        obj = db.query(Producto_model).filter(Producto_model.id_producto == id).first()
        if not obj:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        db.delete(obj)
        db.commit()
        return {"status": "ok", "mensaje": "Producto eliminado"}
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        return {"error": str(e)}