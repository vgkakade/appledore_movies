from ast import alias

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Movies, Genre, Actor, Language


@registry.register_document
class MovieDocument(Document):
    genre = fields.ObjectField(
        properties={
            "name": fields.TextField(),
        }
    )
    language = fields.ObjectField(
        properties={
            "name": fields.TextField(),
        }
    )
    cast = fields.ObjectField(
        properties={
            "name": fields.TextField(),
        }
    )

    class Index:
        name = "products"
        aliases = {"movie_alias": {}}
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
