from sqlalchemy.orm import Session
from common.security import generate_hash_password
from models.User import User
from models.Role import Role
from migrations.factories.UserFactory import UserFactory
from seeders.roles import initial_role


def initial_user(db: Session, is_commit: bool = True) -> User:
    role = db.query(Role).filter(Role.jabatan == "Admin").first()
    if role is None:
        initial_role(db=db, is_commit=is_commit)
    cek_user = (
        db.query(User)
        .filter(User.email == "admin@absensi.py")
        .first()
    )
    if cek_user is not None:
        cek_user.nama = "Admin"
        cek_user.email = "admin@absensi.py"
        cek_user.password = generate_hash_password("12qwaszx")
        cek_user.userRole = role
    else:
        user = UserFactory.create(
            nama="Admin",
            email="admin@absensi.py",
            password=generate_hash_password("12qwaszx"),
            userRole=role,
        )
        db.add(user)
    if is_commit:
        db.commit()
    return user
