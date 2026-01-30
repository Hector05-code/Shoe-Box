from sqlalchemy import Column, Integer, DECIMAL, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla
#from decimal import Decimal

class DetalleVenta(modelo_base_tabla):
    __tablename__ = "detalle_venta"
    __table_args__ = (
        (CheckConstraint("precio_und > 0", name="seguridad_precio_detalle_venta"),
         CheckConstraint("cantidad > 0", name="cantidad_positiva"))
    )

    id_detalle_venta = Column(Integer, primary_key=True, autoincrement=True, index=True,nullable=False)
    id_venta = Column(Integer, ForeignKey("venta.id_venta"), nullable=False)
    id_variante = Column(Integer, ForeignKey("variante.id_variante"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_und = Column(DECIMAL(10,2), nullable=False)
    precio_unitario_usd_snapshot = Column(DECIMAL(10,2), nullable=False)
    cant_devuelta = Column(Integer, nullable=False, default=0)
    
    venta_rel = relationship("Venta", back_populates="detalles")
    variante_rel = relationship("Variante", back_populates="detalles")
    
    @property
    def subtotal_usd(self):
        if self.cantidad and self.precio_unitario_usd_snapshot:
            return self.cantidad * self.precio_unitario_usd_snapshot
        return 0