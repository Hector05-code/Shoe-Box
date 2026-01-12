from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ColorBase(BaseModel):
    nombre: str = Field(max_length=45)
    model_config = ConfigDict(from_attributes=True)
    
class ColorCreate(ColorBase):
    pass

class ColorUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, max_length=45)

class ColorRead(ColorBase):
    id_color: int
    model_config = ConfigDict(from_attributes=True)