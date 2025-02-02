from models import factory_session
from seeders.users import initial_user
from seeders.roles import initial_role
from seeders.shift import initial_shift
from seeders.kehadiran import initial_kehadiran


def initial_seeders():
    with factory_session() as session:
        print("Seeder Role")
        initial_role(db=session, is_commit=False)
        print("Seeder User")
        initial_user(db=session, is_commit=False)
        print("Seeder Shift")
        initial_shift(db=session, is_commit=False)
        print("Seeder Kehadiran")
        initial_kehadiran(db=session, is_commit=False)
        session.commit()
