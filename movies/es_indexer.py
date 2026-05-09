import logging
from datetime import datetime

from django.conf import settings
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk

from movies.models import Movies
from movies.es_document import MovieDocument
from appledore_movies.services.es_movie_serializer import serialize_movie

logger = logging.getLogger(__name__)


def _generate_actions(index_name, chunk_size=1000):
    offset = 0
    while True:
        movies = Movies.objects.prefetch_related("language", "cast", "genre")[
            offset : offset + chunk_size
        ]
        if not movies:
            break

        for movie in movies:
            yield {
                "_index": index_name,
                "_id": movie.id,
                "_source": serialize_movie(movie),
            }

        offset += chunk_size


def bulk_index(movies=None):
    ALIAS = MovieDocument.Index.name
    CHUNK_SIZE = 1000
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    try:
        old_index_name = es.indices.get_alias(name=ALIAS)
        old_index_name = list(old_index_name.keys())[0] if old_index_name else None
    except NotFoundError:
        old_index_name = None

    logger.info(f"Existing index: {old_index_name}")

    new_index_name = f"{ALIAS}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    MovieDocument.init(index=new_index_name)
    logger.info(f"New index created: {new_index_name}")

    logger.info("Indexing data now..")

    try:
        bulk(
            es,
            _generate_actions(new_index_name),
            chunk_size=CHUNK_SIZE,
        )

        logger.info("Data indexed successfully...")

        if old_index_name:
            es.indices.update_aliases(
                {
                    "actions": [
                        {"remove": {"index": old_index_name, "alias": ALIAS}},
                        {"add": {"index": new_index_name, "alias": ALIAS}},
                    ]
                }
            )
            logger.info(f"Switched alias to new index {new_index_name}")
            es.indices.delete(index=old_index_name)
            logger.info(f"Deleted old index {old_index_name}")
        else:
            es.indices.put_alias(index=new_index_name, name=ALIAS)
            logger.info(f"Created new index {new_index_name} with alias '{ALIAS}'")
        logger.info("Indexing Completed!")
    except Exception as e:
        logger.error(f"Indexing failed: {str(e)}")
        es.indices.delete(index=new_index_name, ignore=404)
        logger.error(f"Cleaned up new index {new_index_name} due to failure")
