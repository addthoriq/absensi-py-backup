from sqlalchemy.orm import Session
from models.Shift import Shift
from repository import shift as shift_repo

list_shift = [
    {
        "nama_shift": "Pagi",
        "jam_mulai": "07:00:00",
        "jam_akhir": "12:00:00",
    },
    {
        "nama_shift": "Siang",
        "jam_mulai": "13:00:00",
        "jam_akhir": "17:00:00",
    },
    {
        "nama_shift": "Sore",
        "jam_mulai": "18:00:00",
        "jam_akhir": "22:00:00",
    },
    {
        "nama_shift": "Malam",
        "jam_mulai": "23:00:00",
        "jam_akhir": "06:00:00",
    }
]


def initial_shift(db: Session, is_commit: bool = True):
    for data in list_shift:
        cek_shift = (
            db.query(Shift).filter(
                Shift.nama_shift == data["nama_shift"],
                Shift.jam_mulai == data["jam_mulai"],
                Shift.jam_akhir == data["jam_akhir"]
            ).first()
        )
        if cek_shift is not None:
            cek_shift.nama_shift = data["nama_shift"]
            cek_shift.jam_mulai = data["jam_mulai"]
            cek_shift.jam_akhir = data["jam_akhir"]
        else:
            shift_repo.create(
                db=db,
                nama_shift=data["nama_shift"],
                jam_mulai=data["jam_mulai"],
                jam_akhir=data["jam_akhir"],
                is_commit=False
            )
    if is_commit:
        db.commit()
    return True
