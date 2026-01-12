from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Talla(modelo_base_tabla):
    __tablename__ = "help_talla"

    id_talla = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    nombre = Column(String(45), unique=True, index=True, nullable=False)