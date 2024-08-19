import factory
from core.config.constansts import UserRole
from db.models import CommentModel, PostModel, UserModel


class UserFactory(factory.Factory):
    class Meta:
        model = UserModel

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    role = UserRole.USER
    password = factory.Faker("password")


class PostFactory(factory.Factory):
    class Meta:
        model = PostModel

    title = factory.Faker("sentence")
    content = factory.Faker("text")


class CommentFactory(factory.Factory):
    class Meta:
        model = CommentModel

    content = factory.Faker("text")
