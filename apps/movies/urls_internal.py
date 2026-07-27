from django.urls import path

from .views_internal import reserve_product, release_product

urlpatterns = [
    path("<int:id>/reserve/", reserve_product, name="reserve-product"),
    path("<int:id>/release/", release_product, name="release-product"),
]
