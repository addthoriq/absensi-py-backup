from sqlalchemy.orm import Session
from models.Kehadiran import Kehadiran
from repository import kehadiran as kehadiran_repo

list_kehadiran = [
    {
        "nama_kehadiran": "Hadir",
        "keterangan": "Hadir",
    },
    {
        "nama_kehadiran": "Terlambat",
        "keterangan": "Terlambat",
    },
    {
        "nama_kehadiran": "Alpa",
        "keterangan": "Tidak Hadir",
    },
    {
        "nama_kehadiran": "Cuti",
        "keterangan": "Cuti",
    },
]


def initial_kehadiran(db: Session, is_commit: bool = True):
    for data in list_kehadiran:
        cek_hadir = (
            db.query(Kehadiran)
            .filter(Kehadiran.nama_kehadiran == data["nama_kehadiran"], Kehadiran.keterangan == data["keterangan"])
            .first()
        ) 
        if cek_hadir is not None:
            cek_hadir.nama_kehadiran = data["nama_kehadiran"]
            cek_hadir.keterangan = data["keterangan"]
        else:
            kehadiran_repo.create(
                db=db,
                nama_kehadiran=data["nama_kehadiran"],
                keterangan=data["keterangan"],
                is_commit=False
            )
    if is_commit:
        db.commit()
    return True
