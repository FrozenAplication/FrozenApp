from fastapi import APIRouter, Depends, HTTPException
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

# Modelo para registrar usuario
class RegisterRequest(BaseModel):
    opCode: str
    name: str
    dni: str
    descriptor: str

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return [usuario.__dict__ for usuario in usuarios]

@router.post("/users/register")
def register_user(data: RegisterRequest, db: Session = Depends(get_db)):
    nuevo_usuario = Usuario(
        opCode=data.opCode,
        name=data.name,
        dni=data.dni,
        descriptor=data.descriptor,
        rol="operario"  # por defecto, si no se especifica
    )
    db.add(nuevo_usuario)
    try:
        db.commit()
        return {"status": "success", "msg": "Usuario registrado correctamente."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar usuario: {str(e)}")
