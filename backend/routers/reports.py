from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from datetime import datetime, date
from database import SessionLocal
from models import Usuario, Acceso

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/reports/employee")
def get_employee_report(month: str = None, db: Session = Depends(get_db)):
    try:
        if not month:
            month = datetime.now().strftime("%Y-%m")
        year, month_num = map(int, month.split("-"))
        today = date.today()
        limit_day = today.day if (year == today.year and month_num == today.month) else (
            date(year + (month_num // 12), (month_num % 12) + 1, 1) - date(year, month_num, 1)
        ).days
        workdays = sum(1 for d in range(1, limit_day + 1) if date(year, month_num, d).weekday() < 5)
        usuarios = db.query(Usuario).filter(Usuario.rol != 'admin').all()
        report = {u.id: {"opCode": u.opCode, "name": u.name, "llegadas_tarde": 0, "salidas_tempranas": 0, "faltas": 0, "horas_extras": 0.0} for u in usuarios}
        user_ids = list(report.keys())
        if not user_ids:
            return {"status": "success", "data": []}
        registros = db.query(
            Acceso.usuario_id,
            func.sum(func.case([(func.time(Acceso.fecha_hora_ingreso) > '08:15:00', 1)], else_=0)).label("llegadas_tarde"),
            func.sum(func.case([(func.time(Acceso.fecha_hora_egreso) < '16:00:00', 1)], else_=0)).label("salidas_tempranas"),
            func.sum(func.case([
                (func.time(Acceso.fecha_hora_egreso) >= '17:00:00',
                 func.timestampdiff(func.second, func.time('17:00:00'), func.time(Acceso.fecha_hora_egreso)) + 3600)
            ], else_=0)).label("horas_extras_segundos")
        ).filter(
            extract('year', Acceso.fecha_hora_ingreso) == year,
            extract('month', Acceso.fecha_hora_ingreso) == month_num,
            Acceso.usuario_id.in_(user_ids)
        ).group_by(Acceso.usuario_id).all()
        for r in registros:
            report[r.usuario_id]["llegadas_tarde"] = r.llegadas_tarde
            report[r.usuario_id]["salidas_tempranas"] = r.salidas_tempranas
            report[r.usuario_id]["horas_extras"] = round(r.horas_extras_segundos / 3600, 2)
        presentes = db.query(
            Acceso.usuario_id,
            func.count(func.distinct(func.date(Acceso.fecha_hora_ingreso))).label("dias_presente")
        ).filter(
            extract('year', Acceso.fecha_hora_ingreso) == year,
            extract('month', Acceso.fecha_hora_ingreso) == month_num,
            Acceso.usuario_id.in_(user_ids)
        ).group_by(Acceso.usuario_id).all()
        for p in presentes:
            report[p.usuario_id]["faltas"] = workdays - p.dias_presente
        return {"status": "success", "data": list(report.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")

@router.get("/reports/access-per-day")
def get_access_logs_per_day(fecha: date = date.today(), db: Session = Depends(get_db)):
    try:
        ingresos_por_hora = db.query(
            extract('hour', Acceso.fecha_hora_ingreso).label("hora"),
            func.count(Acceso.id).label("cantidad")
        ).filter(func.date(Acceso.fecha_hora_ingreso) == fecha).group_by("hora").order_by("hora").all()
        egresos_por_hora = db.query(
            extract('hour', Acceso.fecha_hora_egreso).label("hora"),
            func.count(Acceso.id).label("cantidad")
        ).filter(func.date(Acceso.fecha_hora_egreso) == fecha).group_by("hora").order_by("hora").all()
        labels = [f"{h:02d}:00" for h in range(24)]
        ingresos = [0] * 24
        egresos = [0] * 24
        for row in ingresos_por_hora:
            ingresos[int(row.hora)] = row.cantidad
        for row in egresos_por_hora:
            egresos[int(row.hora)] = row.cantidad
        data = {"labels": labels, "ingresos": ingresos, "egresos": egresos}
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener accesos por hora: {str(e)}")

@router.get("/reports/hours-worked-per-day")
def get_hours_worked_per_day(fecha: date = date.today(), db: Session = Depends(get_db)):
    try:
        resultados = db.query(
            Usuario.name.label("nombre_empleado"),
            func.sum(func.extract('epoch', Acceso.fecha_hora_egreso - Acceso.fecha_hora_ingreso)).label("segundos_trabajados")
        ).join(Acceso, Usuario.id == Acceso.usuario_id)         .filter(func.date(Acceso.fecha_hora_ingreso) == fecha, Acceso.fecha_hora_egreso.isnot(None), Usuario.rol != 'admin')         .group_by(Usuario.name).order_by(Usuario.name).all()
        labels = []
        datasets = [{
            "label": "Horas Trabajadas",
            "data": [],
            "backgroundColor": "rgba(75, 192, 192, 0.5)"
        }]
        for r in resultados:
            labels.append(r.nombre_empleado)
            horas = round(r.segundos_trabajados / 3600, 2) if r.segundos_trabajados else 0
            datasets[0]["data"].append(horas)
        return {"status": "success", "data": {"labels": labels, "datasets": datasets}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al calcular horas trabajadas: {str(e)}")

@router.get("/reports/arrival-distribution")
def get_arrival_distribution(fecha: date = date.today(), db: Session = Depends(get_db)):
    try:
        resultados = db.query(
            extract('hour', Acceso.fecha_hora_ingreso).label("hora"),
            func.floor(extract('minute', Acceso.fecha_hora_ingreso) / 15).label("cuarto"),
            func.count(Acceso.id).label("cantidad")
        ).filter(
            func.date(Acceso.fecha_hora_ingreso) == fecha,
            extract('hour', Acceso.fecha_hora_ingreso) >= 7,
            extract('hour', Acceso.fecha_hora_ingreso) < 20
        ).group_by("hora", "cuarto").order_by("hora", "cuarto").all()
        labels = []
        values = []
        for h in range(7, 20):
            for q in range(4):
                minute = q * 15
                labels.append(f"{h:02d}:{minute:02d}")
                values.append(0)
        for r in resultados:
            index = ((int(r.hora) - 7) * 4) + int(r.cuarto)
            if 0 <= index < len(values):
                values[index] = r.cantidad
        return {"status": "success", "data": {"labels": labels, "values": values}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener distribución de llegadas: {str(e)}")

@router.get("/reports/departure-distribution")
def get_departure_distribution(fecha: date = date.today(), db: Session = Depends(get_db)):
    try:
        resultados = db.query(
            extract('hour', Acceso.fecha_hora_egreso).label("hora"),
            func.floor(extract('minute', Acceso.fecha_hora_egreso) / 15).label("cuarto"),
            func.count(Acceso.id).label("cantidad")
        ).filter(
            func.date(Acceso.fecha_hora_egreso) == fecha,
            extract('hour', Acceso.fecha_hora_egreso) >= 7,
            extract('hour', Acceso.fecha_hora_egreso) < 20
        ).group_by("hora", "cuarto").order_by("hora", "cuarto").all()
        labels = []
        values = []
        for h in range(7, 20):
            for q in range(4):
                minute = q * 15
                labels.append(f"{h:02d}:{minute:02d}")
                values.append(0)
        for r in resultados:
            index = ((int(r.hora) - 7) * 4) + int(r.cuarto)
            if 0 <= index < len(values):
                values[index] = r.cantidad
        return {"status": "success", "data": {"labels": labels, "values": values}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener distribución de egresos: {str(e)}")

@router.get("/reports/access-by-type")
def get_access_logs_by_type(fecha: date = date.today(), db: Session = Depends(get_db)):
    try:
        ingresos = db.query(Acceso.tipo_ingreso.label("tipo")).filter(
            Acceso.tipo_ingreso.isnot(None),
            func.date(Acceso.fecha_hora_ingreso) == fecha
        )
        egresos = db.query(Acceso.tipo_egreso.label("tipo")).filter(
            Acceso.tipo_egreso.isnot(None),
            func.date(Acceso.fecha_hora_egreso) == fecha
        )
        union_query = ingresos.union_all(egresos).subquery()
        resultados = db.query(
            union_query.c.tipo,
            func.count().label("total")
        ).group_by(union_query.c.tipo).all()
        labels = []
        values = []
        for r in resultados:
            labels.append(r.tipo.capitalize())
            values.append(r.total)
        return {"status": "success", "data": {"labels": labels, "values": values}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener accesos por tipo: {str(e)}")
