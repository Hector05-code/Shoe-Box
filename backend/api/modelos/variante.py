from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Variante(modelo_base_tabla):
    __tablename__ = "variante"

    id_variante = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    barcode = Column(String(50), unique=True, index=True, nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    id_color = Column(Integer, ForeignKey("help_color.id_color"), nullable=False)
    id_talla = Column(Integer, ForeignKey("help_talla.id_talla"), nullable=False)
    stock_actual = Column(Integer, default=0, nullable=False)
    
    producto_rel = relationship("Producto", back_populates="variantes")
    color_rel = relationship("Color")
    talla_rel = relationship("Talla")
    
    detalles = relationship("DetalleVenta", back_populates="variante_rel")
    movimientos = relationship("Movimiento", back_populates="variante_rel")
    
    
    # idVariante = Column(Integer, primary_key=True, index=True, nullable=False)
    # id_Producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    # color = Column(String(45), nullable=False)
    # talla = Column(String(45), index=True, nullable=False)
    # stock_actual = Column(Integer)
    # producto = Column(String(45), index=True, nullable=False)
    # movimientos = Column(String(45), index=True, nullable=False)
    # detalles = Column(String(45), index=True, nullable=False)
    # producto = relationship("Producto", back_populates="variantes")
    # movimientos = relationship("Movimiento", back_populates="variantes")
    # detalles = relationship("DetalleVenta", back_populates="variantes")