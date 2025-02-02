from . import Base
from sqlalchemy import Column, Integer, String, VARCHAR, ForeignKey, Table
from sqlalchemy.orm import relationship

user_shift = Table(
    'user_shift',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('shift_id', Integer, ForeignKey('shift.id'))
)

class User(Base):
    __tablename__ = "user"

    id = Column("id", Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column("email", VARCHAR(30), nullable=False)
    nama = Column("nama", String(50), nullable=False)
    password = Column("password", String(255), nullable=False)
    role_id = Column("role_id", ForeignKey("role.id"))

    userRole = relationship("Role", backref="user_role", foreign_keys=[role_id])
    userShift = relationship("Shift", secondary=user_shift, back_populates='shiftUser', cascade="all,delete")
