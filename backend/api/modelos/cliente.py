from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Cliente(modelo_base_tabla):
    __tablename__ = "cliente"

    id_cliente_ci = Column(Integer, primary_key=True, autoincrement=False, index=True, nullable=False)
    nombre = Column(String(100), index=True, nullable=False)
    apellido = Column(String(100), index=True, nullable=False)
    telefono = Column(String(45), nullable=False)
    direccion = Column(String(255), nullable=False)
    
    ventas = relationship("Venta", back_populates="cliente_rel")