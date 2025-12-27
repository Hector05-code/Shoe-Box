from sqlalchemy import Column, Integer, String, DECIMAL, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from config_db import modelo_base_tabla

class Detalle_venta(modelo_base_tabla):
    __tablename__ = "detalle_venta"
    __table_args__ = (CheckConstraint("precio_venta > 0", name="precio_antibrutos"))

    id_Detalle_Venta = Column(Integer, primary_key=True, index=True, nullable=False)
    id_venta = Column(Integer, ForeignKey("venta.id_venta"), nullable=False)
    
    linea = Column(String(45), index=True, nullable=False)
    precio_venta = Column(DECIMAL(10,2), nullable=False)
    
    precio = relationship("producto", back_populates="detalle_venta")
    cantidad = Column(Integer(), nullable=False)
    idvariante = Column(Integer(), ForeignKey("variante.idVariante"), nullable=False)