from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from config_db import modelo_base_tabla
import enum

class TipoMovimientoEnum(str, enum.Enum):
    entrada = "Entrada"
    salida = "Salida"
    ajuste = "Ajuste"
    devolucion = "Devolucion"

class Movimiento(modelo_base_tabla):
    __tablename__ = "movimiento"

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    
    id_variante = Column(Integer, ForeignKey("variante.id_variante"), nullable=False)
    id_empleado = Column(Integer, ForeignKey("empleado.id_empleado"), nullable=False)
    cantidad = Column(Integer(), nullable=False)
    tipo_movimiento = Column(Enum(TipoMovimientoEnum), index=True, nullable=False)
    fecha = Column(DateTime(), default=datetime.now, nullable=False)
    
    variante_rel = relationship("Variante", back_populates="movimientos")
    empleado_rel = relationship("Empleado", back_populates="movimientos")
    
    
    # cantidad = Column(Integer(), nullable=False)
    # fecha = Column(DateTime(), nullable=False)
    # id_variante = Column(Integer(), ForeignKey("variante.idVariante"), nullable=False)
    # TipoMovimiento = Column(Enum("Entrada","Salida", name="tipo_movimiento_enum"), index=True, nullable=False)
    # movimiento_Empleado = Column(Integer, ForeignKey("empleado.id_empleado"), nullable=False)
    
    
    #empleado = Column(String(45), index=True, nullable=False)
    #variante = Column(String(45), index=True, nullable=False)
   # empleado = relationship("Empleado", back_populates="movimientos")
    #variante = relationship("Variante", back_populates="movimientos")
    #movimiento empleado debe regresar nombre del empleado
    #movimiento variante debe regresar el nombre de la variante
