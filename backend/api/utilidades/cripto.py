from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt
from passlib.context import CryptContext

# --- CONFIGURACIÓN ARGON2 (La modificación que pediste) ---
# Al usar schemes=["argon2"], Passlib usa automáticamente argon2-cffi.
# Ya no necesitamos el "parche" de compatibilidad de bcrypt.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# --- CONFIGURACIÓN JWT ---
# En producción, esto debería venir de variables de entorno (.env)
SECRET_KEY = "losmasdurosdelsistema"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 1. Función para Encriptar (Hash)
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 2. Función para Verificar (Login)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 3. Función para Crear el Token
def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires = datetime.utcnow() + expires_delta
    else:
        expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt