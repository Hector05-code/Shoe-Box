from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla
import enum

class EmpleadoFuncionEnum(str, enum.Enum):
    GERENTE = "GERENTE"
    EMPLEADO = "EMPLEADO"

class Empleado(modelo_base_tabla):
    __tablename__ = "empleado"

    id_empleado = Column(Integer, primary_key=True, autoincrement=False, index=True, nullable=False)
    nombre = Column(String(100), index=True, nullable=False)
    apellido = Column(String(100), index=True, nullable=False)
    telefono = Column(String(45), nullable=False)
    direccion = Column(String(255), nullable=False)
    usuario = Column(String(50), unique=True, index=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    funcion = Column(Enum(EmpleadoFuncionEnum), index=True, nullable=False)
    estatus = Column(Boolean, default=True, nullable=False)
    
    movimientos = relationship("Movimiento", back_populates="empleado_rel")
    ventas = relationship("Venta", back_populates="empleado_rel")