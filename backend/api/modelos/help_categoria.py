from sqlalchemy import Column, Integer, String
from config_db import modelo_base_tabla
from sqlalchemy.orm import relationship

class Categoria(modelo_base_tabla):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, autoincrement=True, primary_key=True, index=True, nullable=False)
    nombre = Column(String(45), index=True, nullable=False)

    productos = relationship("Producto", back_populates="categoria")
    #tabla opcional