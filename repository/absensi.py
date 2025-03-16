from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from models.Absensi import Absensi
from models.Shift import Shift
from models.User import User
from math import ceil
from typing import Tuple, List, Optional
from datetime import datetime, timedelta
import pytz
from settings import (
    TZ,
    MAX_MINUTE_ABSEN_IN,
    MIN_MINUTE_ABSEN_IN
)

def paginate_list_only_user(
    db: Session,
    user: User,
    page: int = 1,
    page_size: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    jam_masuk: Optional[str] = None,
    jam_keluar: Optional[str] = None,
) -> Tuple[List[Absensi], int, int]:
    limit = page_size
    offset = (page - 1) * limit
    stmt = select(Absensi).filter(Absensi.absen_user == user)
    stmt_count = select(func.count(Absensi.id)).filter(Absensi.absen_user == user)
    if jam_masuk or jam_keluar is not None:
        if jam_masuk:
            jam_masuk = datetime.strptime(jam_masuk, "%H:%M:%S").time()
            stmt = stmt.where(Absensi.jam_masuk == jam_masuk)
            stmt_count = stmt_count.filter(Absensi.jam_masuk == jam_masuk)
        if jam_keluar:
            jam_keluar = datetime.strptime(jam_keluar, "%H:%M:%S").time()
            stmt = stmt.where(Absensi.jam_keluar == jam_keluar)
            stmt_count = stmt_count.filter(Absensi.jam_keluar == jam_keluar)
    if start_date and end_date is not None:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        stmt = stmt.filter(
            and_(
                Absensi.tanggal_absen >= start_date,
                Absensi.tanggal_absen >= end_date,
            )
        )
        stmt_count = stmt_count.filter(
            and_(
                Absensi.tanggal_absen >= start_date,
                Absensi.tanggal_absen >= end_date,
            )
        )
    stmt = stmt.order_by(Absensi.tanggal_absen.asc()).limit(limit=limit).offset(offset=offset)
    get_list = db.execute(stmt).scalars().all()
    num_data = db.execute(stmt_count).scalar()
    num_page = ceil(num_data / limit)
    return get_list, num_data, num_page

def paginate_list_admin(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_name: Optional[str] = None,
    jam_masuk: Optional[str] = None,
    jam_keluar: Optional[str] = None
) -> Tuple[List[Absensi], int, int]:
    limit = page_size
    offset = (page - 1) * limit
    stmt = select(Absensi)
    stmt_count = select(func.count(Absensi.id))
    if user_name is not None:
        stmt = stmt.join(User).filter(User.nama.ilike(f"%{user_name}%"))
        stmt_count = stmt_count.join(User).filter(User.nama.ilike(f"%{user_name}%"))
    if start_date and end_date is not None:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        stmt = stmt.filter(
            and_(
                Absensi.tanggal_absen >= start_date,
                Absensi.tanggal_absen <= end_date,
            )
        )
        stmt_count = stmt_count.filter(
            and_(
                Absensi.tanggal_absen >= start_date,
                Absensi.tanggal_absen <= end_date,
            )
        )
    if jam_masuk or jam_keluar is not None:
        if jam_masuk:
            jam_masuk = datetime.strptime(jam_masuk, "%H:%M:%S").time()
            stmt = stmt.where(Absensi.jam_masuk == jam_masuk)
            stmt_count = stmt_count.filter(Absensi.jam_masuk == jam_masuk)
        if jam_keluar:
            jam_keluar = datetime.strptime(jam_keluar, "%H:%M:%S").time()
            stmt = stmt.where(Absensi.jam_keluar == jam_keluar)
            stmt_count = stmt_count.filter(Absensi.jam_keluar == jam_keluar)
    stmt = stmt.order_by(Absensi.tanggal_absen.asc()).limit(limit=limit).offset(offset=offset)
    get_list = db.execute(stmt).scalars().all()
    num_data = db.execute(stmt_count).scalar()
    num_page = ceil(num_data / limit)
    return get_list, num_data, num_page

def get_by_id(
    db: Session,
    id: int,
) -> Absensi:
    query = select(Absensi).filter(Absensi.id == id)
    data = db.execute(query).scalar()
    return data

def get_absen_without_jam_keluar(
    db: Session,
    user: User
) -> Absensi:
    query = select(Absensi).filter(
        Absensi.absen_user == user,
        Absensi.jam_keluar == None #NOQA
    )
    data = db.execute(query).scalar()
    return data

def get_date_gt_today(
    db: Session,
    user: User
) -> Absensi:
    end_date = datetime.today().date()
    query = select(Absensi).filter(
        Absensi.absen_user == user,
        Absensi.tanggal_absen < end_date,
        Absensi.jam_keluar == None #NOQA
    )
    data = db.execute(query).scalar()
    return data

def forced_absen_gt_today(
    db: Session,
    id: int,
    is_commit: bool = True
):
    query = select(Absensi).filter(
        Absensi.id == id,
    )
    data = db.execute(query).scalar()
    data.jam_keluar = datetime.now().astimezone(tz=pytz.timezone(TZ)).strftime("%H:%M:%S"),
    data.lokasi_keluar = data.lokasi_masuk
    data.keterangan = "Absen lebih dari sehari"
    db.add(data)
    if is_commit:
        db.commit()
    return data

def create_masuk(
    db: Session,
    lokasi_masuk: str,
    userId: User,
    shift: Shift,
    keterangan: Optional[str] = None,
    is_commit: bool = True
) -> Absensi:
    new_data = Absensi(
        shift_id=shift.id,
        tanggal_absen=datetime.today().date(),
        jam_masuk=datetime.now().astimezone(tz=pytz.timezone(TZ)).strftime("%H:%M:%S"),
        keterangan=keterangan,
        lokasi_masuk=lokasi_masuk,
        absen_user=userId,
    )
    db.add(new_data)
    if is_commit:
        db.commit()
    return new_data

def update_exit(
    db: Session,
    id: int,
    shift: Shift,
    lokasi_keluar: str,
    is_commit: bool = True
) -> Absensi:
    query = select(Absensi).filter(
        Absensi.id == id,
        Absensi.jam_keluar == None, #NOQA
        Absensi.shift_id == shift.id
    )
    data = db.execute(query).scalar()
    if data is None:
        return None
    data.jam_keluar = datetime.now().astimezone(tz=pytz.timezone(TZ)).strftime("%H:%M:%S")
    data.lokasi_keluar = lokasi_keluar
    db.add(data)
    if is_commit:
        db.commit()
    return data

def export_excel_admin(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    jam_masuk: Optional[str] = None,
    jam_keluar: Optional[str] = None,
    user_name: Optional[str] = None,
) -> Tuple[List[Absensi], int, int]:
    stmt = select(Absensi)
    if user_name is not None:
        stmt = stmt.join(User).filter(User.nama.ilike(f"%{user_name}%"))
    if start_date and end_date is not None:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        stmt = stmt.filter(
            and_(
                Absensi.tanggal_absen >= start_date,
                Absensi.tanggal_absen <= end_date,
            )
        )
    if jam_masuk or jam_keluar is not None:
        if jam_masuk:
            jam_masuk = datetime.strptime(jam_masuk, "%H:%M:%S").time()
            stmt = stmt.where(Absensi.jam_masuk == jam_masuk)
        if jam_keluar:
            jam_keluar = datetime.strptime(jam_keluar, "%H:%M:%S").time()
            stmt = stmt.where(Absensi.jam_keluar == jam_keluar)
    stmt = stmt.order_by(Absensi.tanggal_absen.desc())
    get_list = db.execute(stmt).scalars().all()
    return get_list


def export_excel_user(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    jam_masuk: Optional[str] = None,
    jam_keluar: Optional[str] = None,
    user: Optional[str] = None,
) -> Tuple[List[Absensi], int, int]:
    stmt = select(Absensi).filter(Absensi.absen_user == user)
    if start_date and end_date is not None:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        stmt = stmt.filter(
            and_(
                Absensi.tanggal_absen >= start_date,
                Absensi.tanggal_absen <= end_date,
            )
        )
    if jam_masuk or jam_keluar is not None:
        if jam_masuk:
            jam_masuk = datetime.strptime(jam_masuk, "%H:%M:%S").time()
            stmt = stmt.where(Absensi.jam_masuk == jam_masuk)
        if jam_keluar:
            jam_keluar = datetime.strptime(jam_keluar, "%H:%M:%S").time()
            stmt = stmt.where(Absensi.jam_keluar == jam_keluar)
    stmt = stmt.order_by(Absensi.tanggal_absen.desc())
    get_list = db.execute(stmt).scalars().all()
    return get_list


def get_absen_by_user_shift(db: Session, user: User, shift: Shift) -> Optional[Absensi]:
    attendance = db.query(Absensi).filter(
        Absensi.user_id == user.id,
        Absensi.shift_id == shift.id
    ).first()
    return attendance
