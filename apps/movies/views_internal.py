from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Movies

MAX_ALLOWED_QUANTITY = 5


@api_view(["POST"])
def reserve_product(request, id):
    try:
        quantity = int(request.data.get("quantity", 1))
        if quantity > MAX_ALLOWED_QUANTITY:
            return Response({"error": f"Stock Unavailable"}, status=400)
        with transaction.atomic():
            product = Movies.objects.select_for_update().get(id=id)
            if product.quantity == 0:
                return Response({"error": "Out of stock"}, status=400)
            elif product.quantity >= quantity:
                product.quantity -= quantity
                product.save()
                return Response(
                    {"message": "Product reserved successfully"}, status=200
                )
            else:
                return Response({"error": "Not enough stock available"}, status=400)
    except Movies.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)
    except (TypeError, ValueError):
        return Response({"error": "Invalid quantity provided."}, status=400)


@api_view(["POST"])
def release_product(request, id):
    """
    Release a reserved product by its ID.
    """
    try:
        ordered_quantity = int(request.data.get("quantity", 1))
        with transaction.atomic():
            product = Movies.objects.select_for_update().get(id=id)
            product.quantity += ordered_quantity
            product.save()
            return Response({"message": "Product released successfully."}, status=200)
    except Movies.DoesNotExist:
        return Response({"error": "Product not found."}, status=404)
    except (TypeError, ValueError):
        return Response({"error": "Invalid quantity provided."}, status=400)
