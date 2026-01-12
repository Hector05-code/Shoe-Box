from sqlalchemy import Column, Integer, String, DECIMAL, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class DetalleVenta(modelo_base_tabla):
    __tablename__ = "detalle_venta"
    __table_args__ = (
        (CheckConstraint("precio_und > 0", name="precio_antibrutos_detalle_venta"),
         CheckConstraint("cantidad > 0", name="cantidad_positiva"))
    )

    id_detalle_venta = Column(Integer, primary_key=True, autoincrement=True, index=True,nullable=False)
    id_venta = Column(Integer, ForeignKey("venta.id_venta"), nullable=False)
    id_variante = Column(Integer, ForeignKey("variante.id_variante"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_und = Column(DECIMAL(10,2), nullable=False)
    
    cant_devuelta = Column(Integer, nullable=False, default=0)
    
    #linea = Column(String(45), index=True, nullable=False)
    
    venta_rel = relationship("Venta", back_populates="detalles")
    variante_rel = relationship("Variante")