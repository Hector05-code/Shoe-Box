from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from config_db import modelo_base_tabla

class Recepcion(modelo_base_tabla):
    __tablename__ = "recepcion"

    id_recepcion = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, default=datetime.now)
    numero_factura_proveedor = Column(String(100), nullable=True)
    proveedor_nombre = Column(String(100), nullable=True)
    observaciones = Column(String(250), nullable=True)
    id_empleado = Column(Integer, ForeignKey("empleado.id_empleado"))
    total_costo_lote_usd = Column(DECIMAL(10,2), default=0.0)
    
    empleado = relationship("Empleado")
    movimientos = relationship("Movimiento", back_populates="recepcion")