from sqlalchemy.orm import Session
from models.Role import Role
from migrations.factories.RoleFactory import RoleFactory

list_role = {"Admin", "Operator", "Guru", "Karyawan"}


def initial_role(db: Session, is_commit: bool = True):
    for data in list_role:
        cek_role = (
            db.query(Role).filter(Role.jabatan == data).first()
        )
        if cek_role is not None:
            cek_role.jabatan = data
        else:
            role = RoleFactory.create(jabatan=data)
        db.add(role)
    if is_commit:
        db.commit()
    return True
