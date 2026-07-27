from django.urls import path

from .views import MovieSearchView, movie_detail
from .views_internal import reserve_product, release_product

urlpatterns = [
    path("", MovieSearchView.as_view(), name="movie-list-search"),
    path("<int:id>/", movie_detail),
]
