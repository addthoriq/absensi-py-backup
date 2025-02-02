import factory
from models import factory_session
from models.Shift import Shift


class ShiftFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Shift
        sqlalchemy_session = factory_session

    jabatan = factory.Faker("name")
