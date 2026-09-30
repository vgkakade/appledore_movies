import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from elasticsearch_dsl import Search

from .serializer import MovieDetailSerializer
from .es_document import MovieDocument
from .models import Movies

logger = logging.getLogger(__name__)


class MovieSearchView(APIView):
    pagination_class = LimitOffsetPagination

    def get(self, request):
        try:
            paginator = self.pagination_class()
            paginator.default_limit = 50
            limit = paginator.get_limit(request)
            offset = paginator.get_offset(request)

            INDEX_ALIAS = MovieDocument.Index.name
            s = Search(index=INDEX_ALIAS).extra(track_total_hits=True)
            s = s.query("match_all")

            # Genre filter
            genres = request.query_params.get("genre", "").strip()
            if genres:
                genre_list = [genre.strip() for genre in genres.split(",")]
                s = s.filter("terms", genre=genre_list)

            # language filter
            languages = request.query_params.get("language", "").strip()
            if languages:
                language_list = [language.strip() for language in languages.split(",")]
                s = s.filter("terms", language=language_list)

            # cast filter
            actors = request.query_params.get("cast", "").strip()
            if actors:
                actor_list = [actor.strip() for actor in actors.split(",")]
                s = s.filter("terms", cast=actor_list)

            status = request.query_params.get("status", "")
            if status:
                s = s.filter("term", status=status)

            s = s[offset : offset + limit]
            response = s.execute()

            results = []
            for hit in response.hits:
                data = hit.to_dict()
                data["id"] = hit.meta.id
                results.append(data)

            paginator.count = response.hits.total.value
            paginator.limit = limit
            paginator.offset = offset
            paginator.request = request
            return paginator.get_paginated_response(results)
        except Exception as e:
            print("ERRPR", str(e))
            return Response(status=500)


@api_view(["GET"])
def movie_detail(request, id):
    try:
        logger.info("Getting produc details", extra={"movie_id": id})
        movie = Movies.objects.prefetch_related("cast", "language", "genre").get(id=id)
        serializer = MovieDetailSerializer(movie)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Movies.DoesNotExist:
        return Response({"data": "No such product"}, status=status.HTTP_404_NOT_FOUND)
