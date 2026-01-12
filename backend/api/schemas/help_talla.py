from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class TallaBase(BaseModel):
    nombre: str = Field(max_length=45)
    model_config = ConfigDict(from_attributes=True)
    
class TallaCreate(TallaBase):
    pass

class TallaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=45)
    
class TallaRead(TallaBase):
    id_talla: int
    model_config = ConfigDict(from_attributes=True)