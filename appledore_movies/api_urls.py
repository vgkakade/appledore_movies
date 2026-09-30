from django.urls import path, include

urlpatterns = [
    path("v1/", include("apps.movies.urls")),
    path("internal/movies/", include("apps.movies.urls_internal")),
]
