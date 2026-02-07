from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from modelos.empleado import Empleado as EmpleadoModel
from utilidades.login import get_db, get_usuario_actual
from utilidades.cripto import verify_pin

def requerir_permiso_gerente(

    x_admin_pin: str | None = Header(default=None, alias="X-Admin-PIN"),
    
    usuario_actual: EmpleadoModel = Depends(get_usuario_actual),
    db: Session = Depends(get_db)
) -> bool:
    
    if usuario_actual.funcion.value == "GERENTE":
        return True

    if not x_admin_pin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Se requiere autorización de un Gerente (Falta PIN)."
        )

    gerentes = db.query(EmpleadoModel).filter(
        EmpleadoModel.funcion == "GERENTE",
        EmpleadoModel.estatus == True
    ).all()

    pin_valido = False
    for gerente in gerentes:
        if gerente.pin_autorizacion and verify_pin(x_admin_pin, gerente.pin_autorizacion):
            pin_valido = True
            break
    
    if not pin_valido:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="PIN de autorización inválido."
        )

    return True