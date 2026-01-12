from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
import bcrypt
#import argon2
from passlib.context import CryptContext # Para encriptar contraseñas
from modelos.empleado import EmpleadoFuncionEnum
from utilidades.login import get_usuario_actual

# Imports locales
from config_db import sesion_local
from modelos.empleado import Empleado as EmpleadoModel
from schemas.empleado import EmpleadoCreate, EmpleadoUpdate, EmpleadoRead

endpoint = APIRouter(prefix="/empleados", tags=["Empleados"])

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Esto maneja el hashing (encriptado) de contraseñas automáticamente
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

# --- SIMULACIÓN DE AUTENTICACIÓN (MOCK) ---
# En el futuro, aquí decodificarás el Token JWT real.
# Por ahora, simulamos que quien llama a la API es un Gerente para probar los permisos.
# def get_usuario_actual():
#     class UsuarioMock:
#         id_empleado = 1
#         usuario = "admin"
#         funcion = "Gerente" # <--- CAMBIA ESTO A "Empleado" PARA PROBAR EL BLOQUEO
#     return UsuarioMock()


# ==========================================
# RUTAS DE LECTURA (Abiertas a usuarios autenticados)
# ==========================================

@endpoint.get("/", response_model=List[EmpleadoRead])
def listar_empleados(db: Session = Depends(get_db)):
    # Aquí podríamos filtrar para que no se vean entre ellos, 
    # pero por ahora listamos todos (sin mostrar contraseñas gracias al Schema Read)
    return db.query(EmpleadoModel).all()

@endpoint.get("/{id}", response_model=EmpleadoRead)
def obtener_empleado(id: int, db: Session = Depends(get_db)):
    empleado = db.query(EmpleadoModel).filter(EmpleadoModel.id_empleado == id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado


# ==========================================
# RUTAS DE ESCRITURA (Solo Gerentes)
# ==========================================

@endpoint.post("/", response_model=EmpleadoRead, status_code=status.HTTP_201_CREATED)
def crear_empleado(
    empleado: EmpleadoCreate, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual),
):
    # 1. Validar Permisos
    if str(usuario_actual.funcion.value) != "Gerente": # Convertimos a str por seguridad
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos."
        )

    # 2. VERIFICACIÓN ROBUSTA (Case Insensitive)
    # Convertimos ambos lados a minúsculas para comparar
    # Asegúrate de usar el nombre EXACTO de la columna en tu Modelo (aquí asumo 'usuario' en minúscula)
    empleado_existente = db.query(EmpleadoModel).filter(
        func.lower(EmpleadoModel.usuario) == empleado.usuario.lower()
    ).first()

    if empleado_existente:
        raise HTTPException(
            status_code=400, 
            detail=f"El usuario '{empleado.usuario}' ya está registrado (verificación previa)."
        )

    try:
        # 3. Encriptación (Directa con bcrypt)
        pass_bytes = empleado.contrasena.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(pass_bytes, salt)
        hashed_string = hashed_bytes.decode('utf-8')
        
        # 4. Creación del Objeto
        # Verifica en modelos/empleado.py si las variables empiezan con Mayúscula o Minúscula
        nuevo_empleado = EmpleadoModel(
            id_empleado=empleado.id_empleado,
            nombre=empleado.nombre,
            apellido=empleado.apellido,
            telefono=empleado.telefono,
            direccion=empleado.direccion,
            usuario=empleado.usuario,
            contrasena=hashed_string,
            funcion=empleado.funcion.value
        )
        
        db.add(nuevo_empleado)
        db.commit()
        db.refresh(nuevo_empleado)
        return nuevo_empleado

    except IntegrityError as e:
        db.rollback()
        # --- AQUÍ ESTÁ LA CLAVE ---
        # e.orig contiene el mensaje original de MySQL (ej: "Column 'nombre' cannot be null")
        print(f"🔥🔥 ERROR REAL DE MYSQL: {e.orig} 🔥🔥") 
        
        # Devolvemos el error técnico al frontend temporalmente para leerlo en el navegador
        raise HTTPException(status_code=400, detail=f"Error de Integridad: {e.orig}")
        
    except Exception as e:
        db.rollback()
        print(f"Error general: {e}") # Imprime en consola para que veas qué pasa
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# @endpoint.post("/", response_model=EmpleadoRead, status_code=status.HTTP_201_CREATED)
# def crear_empleado(
#     empleado: EmpleadoCreate, 
#     db: Session = Depends(get_db),
#     usuario_actual = Depends(get_usuario_actual) # Inyectamos al usuario que hace la petición
# ):
#     # 1. VERIFICACIÓN DE PERMISOS
#     if usuario_actual.funcion != "Gerente":
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, 
#             detail="No tienes permisos de Gerente para crear empleados."
#         )
#     existe = db.query(EmpleadoModel).filter(EmpleadoModel.usuario == empleado.usuario).first()
#     if existe:
#         raise HTTPException(status_code=400, detail="El nombre de Usuario ya existe.")
#     try:
#         # --- ENCRIPTACIÓN DIRECTA Y SEGURA ---
#         pass_bytes = empleado.contrasena.encode('utf-8')
#         salt = bcrypt.gensalt()
#         hashed_bytes = bcrypt.hashpw(pass_bytes, salt)
#         hashed_string = hashed_bytes.decode('utf-8') # Listo para la BD
        
#         nuevo_empleado = EmpleadoModel(
#             nombre=empleado.nombre,
#             usuario=empleado.usuario,
#             contrasena=hashed_string, # Asignamos el hash generado manualmente
#             funcion=empleado.funcion
#         )
        
#         db.add(nuevo_empleado)
#         db.commit()
#         db.refresh(nuevo_empleado)
#         return nuevo_empleado

#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(status_code=400, detail="El nombre de Usuario ya existe.")
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=str(e))


@endpoint.put("/{id}", response_model=EmpleadoRead)
def actualizar_empleado(
    id: int, 
    datos_entrada: EmpleadoUpdate, # Renombrado para evitar conflicto con la clase
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    # 1. VERIFICACIÓN DE PERMISOS
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="Solo los Gerentes pueden editar datos de empleados.")

    # 2. BUSCAR
    empleado_db = db.query(EmpleadoModel).filter(EmpleadoModel.id_empleado == id).first()
    if not empleado_db:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # 3. PREPARAR DATOS
    update_data = datos_entrada.model_dump(exclude_unset=True)

    # 4. CASO ESPECIAL: Si están actualizando la contraseña, hay que encriptarla de nuevo
    # (Nota: Debes haber descomentado 'contrasena' en EmpleadoUpdate si permites esto aquí)
    if "contrasena" in update_data:
        update_data["contrasena"] = pwd_context.hash(update_data["contrasena"])

    # 5. ACTUALIZAR
    for key, value in update_data.items():
        setattr(empleado_db, key, value)

    try:
        db.commit()
        db.refresh(empleado_db)
        return empleado_db
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="El nuevo nombre de Usuario ya está ocupado.")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@endpoint.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_empleado(
    id: int, 
    db: Session = Depends(get_db),
    usuario_actual: EmpleadoRead = Depends(get_usuario_actual)
):
    # 1. VERIFICACIÓN DE PERMISOS
    if usuario_actual.funcion.value != "Gerente":
        raise HTTPException(status_code=403, detail="No tienes permisos.")

    empleado_db = db.query(EmpleadoModel).filter(EmpleadoModel.id_empleado == id).first()
    if not empleado_db:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    # PROTECCIÓN EXTRA: Evitar que el Gerente se elimine a sí mismo
    if empleado_db.id_empleado == usuario_actual.id_empleado:
         raise HTTPException(status_code=400, detail="No puedes eliminar tu propio usuario.")

    try:
        db.delete(empleado_db)
        db.commit()
        return
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))