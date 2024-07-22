import factory
from core.config.constansts import UserRole
from domains.dto.users import UserDTO


class UserFactory(factory.Factory):
    class Meta:
        model = UserDTO

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    role = UserRole.USER
    password = factory.Faker("password")
