from datetime import datetime

from django.core.cache import cache
from django.utils import timezone
from .es_indexer import bulk_index
from .es_document import MovieDocument

from appledore_movies.celery import app
from .models import Movies


@app.task
def sync_products():
    # 1. Read last_synced from redis cache
    # 2. Queries Movies model for updated records
    # 3. Update Elasticsearch index with new/updated records
    # 4. Update last_synced in redis cache
    last_synced = cache.get("last_synced")
    index_name = MovieDocument.Index.name

    if last_synced is None:
        last_synced = timezone.make_aware(datetime(2000, 1, 1))

    sync_started_at = timezone.now()

    updated_movies = Movies.objects.filter(updated_on__gt=last_synced).prefetch_related(
        "genre", "cast", "language"
    )
    if not updated_movies.exists():
        print("No new updates to sync.")
        return
    result = bulk_index(updated_movies, index_name)

    if result:
        cache.set("last_synced", sync_started_at)
        return f"Synced {len(updated_movies)} movies"
    else:
        return "Failed to sync movies"
