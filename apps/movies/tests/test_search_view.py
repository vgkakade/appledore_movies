import pytest
from django.db import connection
from apps.movies.models import Movies


@pytest.mark.django_db
def test_make_movie_fixture(make_movie):
    m = make_movie(title="Coco", quantity=4)
    fetched = Movies.objects.get(title="Coco")
    assert m.id is not None
    assert m.quantity == 4
    assert fetched.id == m.id
