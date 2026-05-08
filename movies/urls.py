from .views import MovieSearchView, movie_detail
from django.urls import path

urlpatterns = [
    path("", MovieSearchView.as_view(), name="movie-list-search"),
    path("<int:id>/", movie_detail),
]
