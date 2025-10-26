from .views import index, movie_detail
from django.urls import path

urlpatterns = [
    path("", index),
    path("<int:id>/", movie_detail),
]
