from django.urls import path, include

from .views import MovieSearchView, movie_detail

urlpatterns = [
    path("", MovieSearchView.as_view(), name="movie-list-search"),
    path("<int:id>/", movie_detail),
    path("internal/", include("apps.movies.internal.urls")),  # Include internal URLs
]
