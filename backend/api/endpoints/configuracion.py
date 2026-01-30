from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config_db import sesion_local
from modelos.configuracion import Configuracion
from utilidades.login import get_db, get_usuario_actual
from schemas.empleado import EmpleadoRead
from schemas.configuracion import ConfiguracionUpdate

endpoint = APIRouter(prefix="/configuracion", tags=["Configuración Sistema"])

# GET
@endpoint.get("/")
def obtener_configuracion(db: Session = Depends(get_db), _: EmpleadoRead = Depends(get_usuario_actual)):
    config = db.query(Configuracion).first()
    if not config:
        config = Configuracion(tasa_dolar=1.0)
        db.add(config)
        db.commit()
    return config

# PUT
@endpoint.put("/tasa")
def actualizar_tasa(
    datos: ConfiguracionUpdate,
    db: Session = Depends(get_db),
    _: EmpleadoRead = Depends(get_usuario_actual)
):
    # if usuario.funcion.value != "GERENTE":
    #     raise HTTPException(status_code=403, detail="No tienes permiso para esta función.")

    config = db.query(Configuracion).first()
    if not config:
        config = Configuracion(id_configuracion=1, tasa_dolar=datos.tasa_dolar)
        db.add(config)
    else:
        config.tasa_dolar = datos.tasa_dolar

    db.commit()
    db.refresh(config)
    return {"mensaje": "Tasa actualizada", "nueva_tasa": config.tasa_dolar}