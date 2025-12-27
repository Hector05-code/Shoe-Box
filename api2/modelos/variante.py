from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Variante(modelo_base_tabla):
    __tablename__ = "variante"

    idVariante = Column(Integer, primary_key=True, index=True, nullable=False)
    id_Producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    color = Column(String(45), nullable=False)
    talla = Column(String(45), index=True, nullable=False)
    stock_actual = Column(Integer)
    
    producto = relationship("Producto", back_populates="variantes")
    movimientos = relationship("Movimiento", back_populates="variante")
    detalles = relationship("DetalleVenta", back_populates="variante")