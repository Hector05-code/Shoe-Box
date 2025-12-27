from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Venta(modelo_base_tabla):
    __tablename__ = "venta"
    
    id_venta = Column(Integer, primary_key=True, index=True, nullable=False)
    id_empleado = Column(Integer, ForeignKey("empleado.id_Empleado") ,index=True, nullable=False)
    id_cliente = Column(Integer, ForeignKey("cliente.id_Cliente_CI"), index=True, nullable=False)
    fecha = Column(DateTime, nullable=False)
    total = Column(DECIMAL(10,2), nullable=False)
    
    detalles = relationship("DetalleVenta", back_populates="venta")