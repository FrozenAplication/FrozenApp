from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
from models import Usuario

router = APIRouter()

# Dependency para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo de entrada para login
class AdminLoginRequest(BaseModel):
    opCode: str
    dni: str

@router.post("/auth/login")
def admin_login(data: AdminLoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(
        Usuario.opCode == data.opCode,
        Usuario.dni == data.dni,
        Usuario.rol == "admin"
    ).first()

    if usuario:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=401, detail="Credenciales de administrador incorrectas.")

