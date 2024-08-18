import factory
from core.config.constansts import UserRole
from db.models.users import UserModel


class UserFactory(factory.Factory):
    class Meta:
        model = UserModel

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    role = UserRole.USER
    password = factory.Faker("password")
