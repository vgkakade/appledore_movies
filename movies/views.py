from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from .es_document import MovieDocument

from django.conf import settings


class MovieSearchView(APIView):
    pagination_class = LimitOffsetPagination

    def get(self, request):
        paginator = self.pagination_class()
        paginator.default_limit = 50
        limit = paginator.get_limit(request)
        offset = paginator.get_offset(request)

        INDEX_ALIAS = MovieDocument.Index.name
        s = Search(index=INDEX_ALIAS).extra(track_total_hits=True)
        s = s.query("match_all")
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


@api_view(["GET"])
def movie_detail(request, id):
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    doc = es.get(index="products", id=id)
    if doc:
        return Response({"id": doc["_id"], **doc["_source"]}, status=status.HTTP_200_OK)

    return Response({"data": "No movie found"}, status=status.HTTP_404_NOT_FOUND)
