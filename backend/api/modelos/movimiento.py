from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from config_db import modelo_base_tabla
import enum

class TipoMovimientoEnum(str, enum.Enum):
    ENTRADA = "Entrada"
    SALIDA = "Salida"
    AJUSTE = "Ajuste"
    DEVOLUCION = "Devolucion"

class Movimiento(modelo_base_tabla):
    __tablename__ = "movimiento"

    id_movimiento = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    
    id_variante = Column(Integer, ForeignKey("variante.id_variante"), nullable=False)
    id_empleado = Column(Integer, ForeignKey("empleado.id_empleado"), nullable=False)
    cantidad = Column(Integer(), nullable=False)
    stock_resultante = Column(Integer(), nullable=False, default=0)
    tipo_movimiento = Column(Enum(TipoMovimientoEnum), index=True, nullable=False)
    fecha = Column(DateTime(), default=datetime.now, nullable=False)
    motivo = Column(String(255), index=True, nullable=True)
    id_recepcion = Column(Integer, ForeignKey("recepcion.id_recepcion"), nullable=True)
    
    variante_rel = relationship("Variante", back_populates="movimientos")
    empleado_rel = relationship("Empleado", back_populates="movimientos")
    recepcion = relationship("Recepcion", back_populates="movimientos")
    