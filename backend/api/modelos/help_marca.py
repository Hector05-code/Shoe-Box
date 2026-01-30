from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Marca(modelo_base_tabla):
    __tablename__ = "marca"

    id_marca = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    estatus = Column(Boolean, default=True)

    productos = relationship("Producto", back_populates="marca_rel")