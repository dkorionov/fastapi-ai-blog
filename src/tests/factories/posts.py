import factory
from db.models import PostModel


class PostFactory(factory.Factory):
    class Meta:
        model = PostModel

    title = factory.Faker("sentence")
    content = factory.Faker("text")