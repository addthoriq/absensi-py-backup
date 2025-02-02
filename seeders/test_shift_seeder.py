from unittest import IsolatedAsyncioTestCase
import alembic.config
from models import factory_session, clear_all_data_on_database
from models.Shift import Shift
from seeders.shift import initial_shift
from sqlalchemy.orm import Session
from sqlalchemy import select


class TestUserRoleUserSeeder(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        alembic_args = ["-c", "alembic.ini", "upgrade", "base"]
        alembic.config.main(argv=alembic_args)
        self.db: Session = factory_session()
        clear_all_data_on_database(self.db)
        return super().setUp()

    async def test_shift_seeder(self):
        # Given
        initial_shift(db=self.db)

        # When
        check_db = self.db.execute(select(Shift)).scalars().all()

        # Expect
        self.assertIsNotNone(check_db)


    def tearDown(self) -> None:
        clear_all_data_on_database(self.db)
        self.db.rollback()
        factory_session.remove()
        return super().tearDown()
