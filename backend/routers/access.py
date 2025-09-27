from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from database import SessionLocal
from models import Acceso

router = APIRouter()

# Dependency para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo de datos para la solicitud
class AccessRequest(BaseModel):
    usuario_id: int
    accion: str  # 'ingreso' o 'egreso'
    tipo: str = "desconocido"
    fecha_hora: datetime = datetime.now()

@router.post("/access")
def registrar_acceso(data: AccessRequest, db: Session = Depends(get_db)):
    usuario_id = data.usuario_id
    accion = data.accion
    tipo = data.tipo
    fecha_hora = data.fecha_hora

    if not usuario_id or not accion:
        raise HTTPException(status_code=400, detail="Faltan datos para registrar acceso.")

    if accion == "ingreso":
        # Verificar si ya tiene un ingreso sin egreso
        existing = db.query(Acceso).filter(
            Acceso.usuario_id == usuario_id,
            Acceso.fecha_hora_egreso == None
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Usted ya ha registrado su ingreso.")

        nuevo_acceso = Acceso(
            usuario_id=usuario_id,
            fecha_hora_ingreso=fecha_hora,
            tipo_ingreso=tipo
        )
        db.add(nuevo_acceso)
        db.commit()
        return {"status": "success", "msg": "Ingreso registrado correctamente."}

    elif accion == "egreso":
        acceso = db.query(Acceso).filter(
            Acceso.usuario_id == usuario_id,
            Acceso.fecha_hora_egreso == None
        ).order_by(Acceso.fecha_hora_ingreso.desc()).first()

        if not acceso:
            raise HTTPException(status_code=400, detail="Debe registrar su ingreso antes de poder egresar.")

        acceso.fecha_hora_egreso = fecha_hora
        acceso.tipo_egreso = tipo
        db.commit()
        return {"status": "success", "msg": "Egreso registrado correctamente."}

    else:
        raise HTTPException(status_code=400, detail="Acción no válida.")
