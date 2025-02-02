from unittest import IsolatedAsyncioTestCase
import alembic.config
from models import factory_session, clear_all_data_on_database
from models.Kehadiran import Kehadiran
from seeders.kehadiran import initial_kehadiran
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
        initial_kehadiran(db=self.db)

        # When
        check_db = self.db.execute(select(Kehadiran)).scalars().all()

        # Expect
        self.assertIsNotNone(check_db)


    def tearDown(self) -> None:
        clear_all_data_on_database(self.db)
        self.db.rollback()
        factory_session.remove()
        return super().tearDown()
