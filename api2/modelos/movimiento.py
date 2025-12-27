from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Movimiento(modelo_base_tabla):
    __tablename__ = "movimiento"

    id_Movimiento = Column(Integer, primary_key=True, index=True, nullable=False)
    cantidad = Column(Integer(), nullable=False)
    fecha = Column(DateTime(), nullable=False)
    id_variante = Column(Integer(), ForeignKey("variante.idVariante"), nullable=False)
    TipoMovimiento = Column(Enum("Entrada","Salida", name="tipo_movimiento_enum"), index=True, nullable=False)
    movimiento_Empleado = Column(Integer, ForeignKey("empleado.id_empleado", nullable=False))
    empleado = relationship("Empleado", back_populates="movimientos")
    variante = relationship("Variante", back_populates="movimientos")
