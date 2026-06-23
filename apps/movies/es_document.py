from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Movies, Genre, Actor, Language


@registry.register_document
class MovieDocument(Document):
    genre = fields.KeywordField(multi=True)
    language = fields.KeywordField(multi=True)
    cast = fields.KeywordField(multi=True)

    class Index:
        name = "products"
        aliases = {"movies": {}}
        settings = {
            "number_of_shards": 2,
            "number_of_replicas": 1,
        }

    class Django:
        model = Movies
        fields = [
            "id",
            "title",
            "description",
            "release_date",
            "price",
            "rating",
        ]
        related_models = [Genre, Actor, Language]
