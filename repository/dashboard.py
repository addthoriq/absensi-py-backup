from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from models.Absensi import Absensi
from models.User import User
from datetime import datetime

def count_day_admin(
    db: Session,
    start_date: str,
    end_date: str,
) -> int:
    stmt_count = select(func.count(Absensi.id))
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    stmt_count = stmt_count.filter(
        and_(
            Absensi.tanggal_absen >= start_date,
            Absensi.tanggal_absen <= end_date,
        )
    )
    num_data = db.execute(stmt_count).scalar()
    return num_data

def count_day_user(
    db: Session,
    user: User,
    start_date: str,
    end_date: str,
) -> int:
    stmt_count = select(func.count(Absensi.id)).filter(Absensi.absen_user == user)
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    stmt_count = stmt_count.filter(
        and_(
            Absensi.tanggal_absen >= start_date,
            Absensi.tanggal_absen <= end_date,
        )
    )
    num_data = db.execute(stmt_count).scalar()
    return num_data

def volume_by_month_admin(
    db: Session,
    start_date: str,
    end_date: str,
):
    stmt = select(Absensi.tanggal_absen, func.count(Absensi.id))
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    stmt = stmt.filter(
        and_(
            Absensi.tanggal_absen >= start_date,
            Absensi.tanggal_absen <= end_date,
        )
    )
    stmt = stmt.group_by(Absensi.tanggal_absen).order_by(Absensi.tanggal_absen.asc())
    data = db.execute(stmt).all()
    return data

def volume_by_month_user(
    db: Session,
    user: User,
    start_date: str,
    end_date: str,
):
    stmt = select(Absensi.tanggal_absen, func.count(Absensi.id)).filter(Absensi.absen_user == user)
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    stmt = stmt.filter(
        and_(
            Absensi.tanggal_absen >= start_date,
            Absensi.tanggal_absen <= end_date,
        )
    )
    stmt = stmt.group_by(Absensi.tanggal_absen).order_by(Absensi.tanggal_absen.asc())
    data = db.execute(stmt).all()
    return data