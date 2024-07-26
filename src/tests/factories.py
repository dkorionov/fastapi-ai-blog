import factory
from core.config.constansts import UserRole
from domains.dto import PostDTO, UserDTO


class UserFactory(factory.Factory):
    class Meta:
        model = UserDTO

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    role = UserRole.USER
    password = factory.Faker("password")


class PostFactory(factory.Factory):
    class Meta:
        model = PostDTO
        strategy = factory.BUILD_STRATEGY

    title = factory.Faker("sentence")
    content = factory.Faker("text")
