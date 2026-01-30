from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, DECIMAL, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from config_db import modelo_base_tabla

class Venta(modelo_base_tabla):
    __tablename__ = "venta"
    
    id_venta = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    id_empleado = Column(Integer, ForeignKey("empleado.id_empleado"), index=True, nullable=False)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente_ci"), index=True, nullable=False)
    fecha = Column(DateTime, server_default=func.now(), nullable=False) 
    tasa_dolar_snapshot = Column(DECIMAL(10,2), nullable=False)
    subtotal_usd = Column(DECIMAL(10,2), nullable=False, default=0.00)
    monto_iva_usd = Column(DECIMAL(10,2), nullable=False, default=0.00)
    monto_igtf_usd = Column(DECIMAL(10,2), nullable=False, default=0.00)   
    total_venta_usd = Column(DECIMAL(10,2), nullable=False)
    total_venta_bolivares = Column(DECIMAL(10,2), nullable=False)
    descuento_porcentaje = Column(DECIMAL(5,2), nullable=True)
    motivo_descuento = Column(String(255), nullable=True)
    
    detalles = relationship("DetalleVenta", back_populates="venta_rel", cascade="all, delete-orphan")
    
    cliente_rel = relationship("Cliente") 
    empleado_rel = relationship("Empleado")