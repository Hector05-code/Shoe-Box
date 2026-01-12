import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import bcrypt
bcrypt.__about__ = type('type', (object,), {})()
bcrypt.__about__.__version__ = bcrypt.__version__

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from passlib.context import CryptContext
from modelos import (
    cliente,
    detalle_venta,
    empleado,
    help_categoria,
    help_color,
    help_talla,
    movimiento,
    producto,
    variante,
    venta
)
from config_db import engine, sesion_local, modelo_base_tabla
from modelos.empleado import Empleado
from endpoints import (
    auth,
    cliente, 
    detalle_venta, 
    empleado, 
    help_categoria, 
    help_color, 
    help_talla, 
    movimiento, 
    producto, 
    variante, 
    venta) 

modelo_base_tabla.metadata.create_all(bind=engine)
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def crear_admin():
    session = sesion_local()
    try:
        admin = session.query(Empleado).filter(Empleado.usuario == "admin").first()
        
        if not admin:
            password_bytes = "admin123".encode('utf-8')
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            nuevo_admin = Empleado(
                id_empleado=1,
                nombre="Admin",
                apellido="n/a",
                telefono="n/a",
                direccion="n/a",
                usuario="admin",
                contrasena=hashed.decode('utf-8'),
                funcion="Gerente"
            )
            session.add(nuevo_admin)
            session.commit()
            print("Usuario administrador creado con éxito: User='admin' | Contraseña='admin123'")
        else:
            print("Ya existe un administrador. Saltando creación.")
            
    except Exception as e:
        print(f"Error al intentar crear admin: {e}")
    finally:
        session.close()

crear_admin()

app = FastAPI(
    title="Sistema de Inventario para ShoeBox",
    description="Desarrollado por los más duros del sistema",
    debug=True)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://localhost:8000",
    "http://localhost:3306",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cliente.endpoint)
app.include_router(detalle_venta.endpoint)
app.include_router(empleado.endpoint)
app.include_router(help_categoria.endpoint)
app.include_router(help_color.endpoint)
app.include_router(help_talla.endpoint)
app.include_router(movimiento.endpoint)
app.include_router(producto.endpoint)
app.include_router(variante.endpoint)
app.include_router(venta.endpoint)
app.include_router(auth.endpoint)

@app.get("/")
def arranque():
    return {
        "mensaje": "Bienvenido al API de ShoeBox"}