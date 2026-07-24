from django.urls import path, include

urlpatterns = [
    path("v1/", include("apps.movies.urls")),
    path("<int:id>/reserve/", include("apps.movies.views_internal")),
    path("<int:id>/release/", include("apps.movies.views_internal")),
]
