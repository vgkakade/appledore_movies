from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .serializer import MovieSerializer, MovieDetailSerializer
from .models import Movies


# Create your views here.
@api_view(["GET"])
def index(request):
    movies = Movies.objects.all()
    if movies:
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"data": "No movies"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def movie_detail(request, id):
    try:
        movie = Movies.objects.get(id=id)
    except Movies.DoesNotExist:
        return Response({"data": "No movie found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = MovieDetailSerializer(movie)
    return Response(serializer.data, status=status.HTTP_200_OK)
