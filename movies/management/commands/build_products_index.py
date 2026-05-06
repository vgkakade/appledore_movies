from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

from elasticsearch import Elasticsearch, NotFoundError

from movies.es_document import MovieDocument
from movies.models import Movies
from appledore_movies.services.es_movie_serializer import serialize_movie


class Command(BaseCommand):
    help = "Create Elasticsearch index for Products"

    def handle(self, *args, **options):
        es = Elasticsearch(settings.ELASTICSEARCH_HOST)
        ALIAS = MovieDocument.Index.name
        try:
            old_index_name = es.indices.get_alias(name=ALIAS)
            old_index_name = list(old_index_name.keys())[0] if old_index_name else None
        except NotFoundError:
            old_index_name = None

        self.stdout.write(self.style.NOTICE(f"Existing index: {old_index_name}"))

        new_index_name = f"{ALIAS}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        MovieDocument.init(index=new_index_name)
        self.stdout.write(self.style.SUCCESS("New Index created successfully...\n"))

        self.stdout.write("Indexing data now..")
        for movie in Movies.objects.all():
            doc = MovieDocument(meta={"id": movie.id}, **serialize_movie(movie))
            doc.save(index=new_index_name)
        self.stdout.write(self.style.SUCCESS("Data indexed successfully...\n"))

        if old_index_name:
            es.indices.update_aliases(
                {
                    "actions": [
                        {"remove": {"index": old_index_name, "alias": ALIAS}},
                        {"add": {"index": new_index_name, "alias": ALIAS}},
                    ]
                }
            )
            self.stdout.write(
                self.style.SUCCESS(f"Switched alias to new index {new_index_name}")
            )
            es.indices.delete(index=old_index_name)
            self.stdout.write(self.style.SUCCESS(f"Deleted old index {old_index_name}"))
        else:
            es.indices.put_alias(index=new_index_name, name=ALIAS)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created new index {new_index_name} with alias '{ALIAS}'"
                )
            )
        self.stdout.write(self.style.SUCCESS("Indexing Completed!"))
