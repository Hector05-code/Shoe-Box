from sqlalchemy import Column, Integer, String
#from sqlalchemy.orm import Relationship
from config_db import modelo_base_tabla

class Cliente(modelo_base_tabla):
    __tablename__ = "cliente"

    id_Cliente_CI = Column(Integer, primary_key=True, index=True, nullable=False)
    Nombre = Column(String(45), index=True, nullable=False)
    Apellido = Column(String(45), index=True, nullable=False)
    Telefono = Column(String(45), nullable=False)
    Direccion = Column(String(45), nullable=False)