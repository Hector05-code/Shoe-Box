from sqlalchemy import Column, Integer, String, Float, DECIMAL, CheckConstraint, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Producto(modelo_base_tabla):
    __tablename__ = "producto"
    __table_args__ = (CheckConstraint("precio_venta > 0", name="precio_antibrutos_venta"),)

    id_producto = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    nombre = Column(String(145), index=True, nullable=False)
    marca = Column(String(45), index=True, nullable=False)
    precio_venta = Column(DECIMAL(10,2), nullable=False)
    
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)
    estatus = Column(Boolean, default=True, nullable=False)
    categoria = relationship("Categoria", back_populates="productos")
    
    variantes = relationship("Variante", back_populates="producto_rel", cascade="all, delete-orphan") #verificar nombre en BD
    