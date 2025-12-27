from sqlalchemy import Column, Integer, String, Float, DECIMAL, CheckConstraint
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Producto(modelo_base_tabla):
    __tablename__ = "producto"
    __table_args__ = (CheckConstraint("precio_venta > 0", name="precio_antibrutos"))

    id_producto = Column(Integer, primary_key=True, index=True, nullable=False)
    #codigo_barra = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(145), index=True, nullable=False)
    marca = Column(String(45), index=True, nullable=False)
    categoria = Column(String(45), index=True, nullable=False)
    precio_venta = Column(DECIMAL(10,2), nullable=False)
    
    variantes = relationship("Variante", back_populates="producto")
    detalles = relationship("DetalleVenta", back_populates="producto")