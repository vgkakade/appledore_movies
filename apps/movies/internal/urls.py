from django.urls import path

from .views import reserve_product, release_product, get_products

urlpatterns = [
    path("<int:id>/reserve/", reserve_product),
    path("<int:id>/release/", release_product),
    path("products/", get_products),
]
