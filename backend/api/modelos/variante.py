from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Boolean
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Variante(modelo_base_tabla):
    __tablename__ = "variante"

    id_variante = Column(Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    barcode = Column(String(50), unique=True, index=True, nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto", ondelete="CASCADE"), nullable=False)
    id_color = Column(Integer, ForeignKey("color.id_color"), nullable=False)
    id_talla = Column(Integer, ForeignKey("help_talla.id_talla"), nullable=False)
    stock_actual = Column(Integer, default=0, nullable=False)
    stock_minimo = Column(Integer, default=5, nullable=False)
    costo_usd_esp = Column(DECIMAL(10,2), nullable=True)
    precio_venta_usd_esp = Column(DECIMAL(10,2), nullable=True)
    estatus = Column(Boolean, default=True, nullable=False)
    
    producto_rel = relationship("Producto", back_populates="variantes")
    color_rel = relationship("Color")
    talla_rel = relationship("Talla")
    
    detalles = relationship("DetalleVenta", back_populates="variante_rel")
    movimientos = relationship("Movimiento", back_populates="variante_rel")