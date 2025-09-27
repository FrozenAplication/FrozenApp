from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    opCode = Column(String)
    name = Column(String)
    dni = Column(String)
    descriptor = Column(String)
    rol = Column(String)

class Acceso(Base):
    __tablename__ = "accesos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    fecha_hora_ingreso = Column(DateTime)
    fecha_hora_egreso = Column(DateTime)
    tipo_ingreso = Column(String)
    tipo_egreso = Column(String)
