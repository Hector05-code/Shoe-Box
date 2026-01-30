from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from modelos.empleado import Empleado as EmpleadoModel
from utilidades.cripto import verify_password, create_access_token
from utilidades.login import get_db

endpoint = APIRouter(tags=["Login"])

@endpoint.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    empleado = db.query(EmpleadoModel).filter(EmpleadoModel.usuario == form_data.username).first()
    
    if not empleado or not verify_password(form_data.password, empleado.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=empleado.usuario)
    
    return {"access_token": access_token, "token_type": "bearer"}