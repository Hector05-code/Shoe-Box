from sqlalchemy import Column, Integer, ForeignKey, DateTime, DECIMAL, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from config_db import modelo_base_tabla

class Venta(modelo_base_tabla):
    __tablename__ = "venta"
    
    id_venta = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    
    # FOREIGN KEYS
    # Asegúrate de que coincidan con los nombres exactos en las tablas Cliente y Empleado
    id_empleado = Column(Integer, ForeignKey("empleado.id_empleado"), index=True, nullable=False)
    id_cliente = Column(Integer, ForeignKey("cliente.id_cliente_ci"), index=True, nullable=False)
    
    # DATOS
    # func.now() deja que la base de datos ponga la hora exacta del servidor
    fecha = Column(DateTime, server_default=func.now(), nullable=False) 
    total = Column(DECIMAL(10,2), nullable=False)
    
    # RELACIONES
    detalles = relationship("DetalleVenta", back_populates="venta_rel")
    
    # Relaciones opcionales para acceder a datos del cliente/empleado desde la venta
    cliente_rel = relationship("Cliente") 
    empleado_rel = relationship("Empleado")