from django.core.management.base import BaseCommand

from movies.es_indexer import re_index


class Command(BaseCommand):
    help = "Create Elasticsearch index for Products"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Started Indexing..."))
        re_index()
        self.stdout.write(self.style.NOTICE("Indexing Completed!"))
