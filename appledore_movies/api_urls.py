from django.urls import path, include

urlpatterns = [
    path("v1/", include("apps.movies.urls")),
    path("internal/", include("apps.movies.internal.urls")),
]
