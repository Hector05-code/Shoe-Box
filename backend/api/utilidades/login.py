# utils/dependencias.py (o donde tengas get_usuario_actual)
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.empleado import Empleado
from utilidades.cripto import SECRET_KEY, ALGORITHM

# Esta url debe coincidir con la de tu endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_db():
    db = sesion_local()
    try:
        yield db
    finally:
        db.close()

def get_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    exception_auth = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificamos el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise exception_auth
    except JWTError:
        raise exception_auth
    
    # Buscamos al usuario en la BD
    usuario = db.query(Empleado).filter(Empleado.usuario == username).first()
    if usuario is None:
        raise exception_auth
        
    return usuario