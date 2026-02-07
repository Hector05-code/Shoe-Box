import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from fastapi import FastAPI
from utilidades.cripto import get_password_hash, get_pin_hash
from fastapi.middleware.cors import CORSMiddleware
from config_db import engine, sesion_local, modelo_base_tabla
from modelos import (
    cliente,
    configuracion,
    detalle_venta,
    empleado,
    help_categoria,
    help_color,
    help_marca,
    help_talla,
    movimiento,
    producto,
    recepcion,
    variante,
    venta
)
from modelos.empleado import Empleado as EmpleadoModel, EmpleadoFuncionEnum
from endpoints import (
    auth,
    cliente,
    configuracion, 
    detalle_venta, 
    empleado, 
    help_categoria, 
    help_color, 
    help_marca,
    help_talla, 
    movimiento, 
    producto,
    recepcion,
    reporte, 
    variante, 
    venta) 

modelo_base_tabla.metadata.create_all(bind=engine)

def crear_admin():
    session = sesion_local()
    try:
        admin = session.query(EmpleadoModel).filter(EmpleadoModel.usuario == "admin").first()
        
        if not admin:

            nuevo_admin = EmpleadoModel(
                id_empleado=1,
                nombre="Admin",
                apellido="n/a",
                telefono="n/a",
                direccion="n/a",
                usuario="admin",
                contrasena=get_password_hash("admin123"),
                funcion=EmpleadoFuncionEnum.GERENTE,
                pin_autorizacion=get_pin_hash("1234"),
                estatus=True
            )
            session.add(nuevo_admin)
            session.commit()
            print("Usuario administrador creado con éxito: User='admin' | Contraseña='admin123' | PIN='1234'")
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

app.include_router(auth.endpoint)
app.include_router(cliente.endpoint)
app.include_router(configuracion.endpoint)
app.include_router(detalle_venta.endpoint)
app.include_router(empleado.endpoint)
app.include_router(help_categoria.endpoint)
app.include_router(help_color.endpoint)
app.include_router(help_marca.endpoint)
app.include_router(help_talla.endpoint)
app.include_router(movimiento.endpoint)
app.include_router(producto.endpoint)
app.include_router(recepcion.endpoint)
app.include_router(reporte.endpoint)
app.include_router(variante.endpoint)
app.include_router(venta.endpoint)
app.include_router(auth.endpoint)

@app.get("/")
def arranque():
    return {
        "mensaje": "Bienvenido al API de ShoeBox"}