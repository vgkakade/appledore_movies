import pytest
from rest_framework.test import APIClient

from apps.movies.models import Movies, Genre, Language, Actor


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def make_movie(db):
    def _make(
        genres=("Drama",),
        languages=("English",),
        cast=("Leonardo DiCaprio",),
        **overrides
    ):
        data = dict(
            title="Inception",
            release_date="2010-07-16",
            duration=148,
            description="A thief enters dreams.",
            price=9.99,
            poster="https://example.com/inception.jpg",
            trailer_url="https://www.youtube.com/watch?v=YoHD9XEInc0",
            rating=8.8,
            added_on="2025-01-17T03:11:29.557Z",
            updated_on="2025-02-17T03:11:29.557Z",
            quantity=10,
            status="active",
        )
        data.update(overrides)
        movie = Movies.objects.create(**data)
        movie.genre.set([Genre.objects.get_or_create(name=n)[0] for n in genres])
        movie.language.set(
            [Language.objects.get_or_create(name=n)[0] for n in languages]
        )
        movie.cast.set([Actor.objects.get_or_create(name=n)[0] for n in cast])
        return movie

    return _make
