import factory
from core.config.constansts import UserRole
from services.schemas.user import BaseUser


class UserFactory(factory.Factory):
    class Meta:
        model = BaseUser

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    role = UserRole.USER
    password = factory.Faker("password")
