from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Movies, Genre, Actor, Language


@registry.register_document
class MovieDocument(Document):
    genre = fields.KeywordField(multi=True, normalizer="lowercase_normalizer")
    language = fields.KeywordField(multi=True, normalizer="lowercase_normalizer")
    cast = fields.KeywordField(multi=True, normalizer="lowercase_normalizer")
    status = fields.KeywordField(normalizer="lowercase_normalizer")

    class Index:
        name = "products"
        aliases = {"movies": {}}
        settings = {
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "analysis": {
                "normalizer": {
                    "lowercase_normalizer": {"type": "custom", "filter": ["lowercase"]}
                }
            },
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
