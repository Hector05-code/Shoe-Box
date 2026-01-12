# endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.empleado import Empleado as EmpleadoModel
from utilidades.cripto import verify_password, create_access_token

endpoint = APIRouter(tags=["Login"])

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

@endpoint.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Buscar usuario
    # form_data.username contiene lo que el usuario escriba en el campo de usuario
    empleado = db.query(EmpleadoModel).filter(EmpleadoModel.usuario == form_data.username).first()
    
    # 2. Validar usuario y contraseña
    if not empleado or not verify_password(form_data.password, empleado.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Generar Token
    # Guardamos el ID del empleado en el token ("sub")
    access_token = create_access_token(subject=empleado.usuario)
    
    # 4. Retornar respuesta estándar OAuth2
    return {"access_token": access_token, "token_type": "bearer"}