import logging
from datetime import datetime

from django.conf import settings
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk

from .models import Movies
from .es_document import MovieDocument
from appledore_movies.services.es_movie_serializer import serialize_movie

logger = logging.getLogger(__name__)
CHUNK_SIZE = 1000


def _generate_actions(updated_movies, index_name):
    offset_start = 0
    while True:
        offset_end = offset_start + CHUNK_SIZE
        batch = updated_movies[offset_start:offset_end]
        if not batch:
            print(f"No data for offset {offset_start} to {offset_end}")
            break

        for movie in batch:
            yield {
                "_index": index_name,
                "_id": movie.id,
                "_source": serialize_movie(movie),
            }

        offset_start += CHUNK_SIZE


def bulk_index(updated_movies, index_name):
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    logger.info("Bulk Indexing start..")
    try:
        bulk(
            client=es,
            actions=_generate_actions(updated_movies, index_name),
            chunk_size=CHUNK_SIZE,
        )
        logger.info("Bulk Indexing end...")
        return True
    except Exception as e:
        logger.error(f"Bulk Indexing failed: {str(e)}")
        return False


def re_index():
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    ALIAS = MovieDocument.Index.name
    try:
        old_index_name = es.indices.get_alias(name=ALIAS)
        old_index_name = list(old_index_name.keys())[0] if old_index_name else None
    except NotFoundError:
        old_index_name = None

    logger.info(f"Current index: {old_index_name}")
    new_index_name = f"{ALIAS}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        MovieDocument.init(index=new_index_name)
        logger.info(f"New index created: {new_index_name}")

        movies = Movies.objects.prefetch_related("language", "cast", "genre")
        result = bulk_index(movies, new_index_name)

        if not result:
            raise Exception("Bulk indexing failed")

        if old_index_name:
            body = {
                "actions": [
                    {"remove": {"index": old_index_name, "alias": ALIAS}},
                    {"add": {"index": new_index_name, "alias": ALIAS}},
                ]
            }
            es.indices.update_aliases(body=body)
            logger.info(f"Assigned alias {ALIAS} to index: {new_index_name}")
            es.indices.delete(index=old_index_name)
            logger.info(f"Deleted old index: {old_index_name}")
        else:
            es.indices.put_alias(index=new_index_name, name=ALIAS)
            logger.info(f"Created new index {new_index_name} with alias {ALIAS}")
        logger.info("Re-indexing Completed!")
    except Exception as e:
        logger.error(f"Reindex failed: {str(e)}")
        es.indices.delete(index=new_index_name, ignore=404)
