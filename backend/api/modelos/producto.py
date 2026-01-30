from sqlalchemy import Column, Integer, String, DECIMAL, CheckConstraint, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Producto(modelo_base_tabla):
    __tablename__ = "producto"
    __table_args__ = (CheckConstraint("precio_venta_usd > 0", name="seguridad_precio_venta_usd"),
                      CheckConstraint("costo_usd >= 0", name="seguridad_costo_usd"),)

    id_producto = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    nombre = Column(String(145), index=True, nullable=False)
    costo_usd = Column(DECIMAL(10,2), nullable=False, default=0.00)
    precio_venta_usd = Column(DECIMAL(10,2), nullable=False)
    aplica_iva = Column(Boolean, default=True, nullable=False)
    
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), index=True, nullable=False)
    id_marca = Column(Integer, ForeignKey("marca.id_marca"), index=True, nullable=False)
    estatus = Column(Boolean, default=True, nullable=False)
    
    categoria_rel = relationship("Categoria", back_populates="productos")
    marca_rel = relationship("Marca", back_populates="productos")
    variantes = relationship("Variante", back_populates="producto_rel", cascade="all, delete-orphan")
    