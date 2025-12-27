from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Empleado(modelo_base_tabla):
    __tablename__ = "empleado"

    id_Empleado = Column(Integer, primary_key=True, index=True, nullable=False)
    Nombre = Column(String(45), index=True, nullable=False)
    Apellido = Column(String(45), index=True, nullable=False)
    Telefono = Column(String(45), nullable=False)
    #Direccion = Column(String(45), nullable=False)
    Usuario = Column(String(45), nullable=False)
    Contraseña = Column(String(45), nullable=False)
    Funcion = Column(String(45), nullable=False)
    movimientos = relationship("Movimiento", back_populates="empleado")