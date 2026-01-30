from sqlalchemy import Column, Integer, DECIMAL, DateTime
from datetime import datetime
from config_db import modelo_base_tabla

class Configuracion(modelo_base_tabla):
    __tablename__="configuracion"
    id_configuracion = Column(Integer, primary_key=True, autoincrement=True, index=True)
    tasa_dolar = Column(DECIMAL(10,2), nullable=False, default=1.0)
    iva_porcentaje = Column(DECIMAL(10,2), nullable=False, default=0.16)
    igtf_porcentaje = Column(DECIMAL(10,2), nullable=False, default=0.03)
    fecha_actualizacion = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    