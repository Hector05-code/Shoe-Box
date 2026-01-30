from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime

class ConfiguracionUpdate(BaseModel):
    tasa_dolar: Decimal

class ConfiguracionRead(BaseModel):
    tasa_dolar: Decimal 
    iva_porcentaje: Decimal
    igtf_porcentaje: Decimal
    fecha_actualizacion: datetime

    model_config = ConfigDict(from_attributes=True)