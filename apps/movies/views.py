import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from elasticsearch_dsl import Search, Q

from .serializer import MovieDetailSerializer
from .es_document import MovieDocument
from .models import Movies

logger = logging.getLogger(__name__)


class MovieSearchView(APIView):
    pagination_class = LimitOffsetPagination

    def get(self, request):
        SORTABLE = {"rating", "price", "release_date"}
        paginator = self.pagination_class()
        paginator.default_limit = 50
        limit = paginator.get_limit(request)
        offset = paginator.get_offset(request)

        INDEX_ALIAS = MovieDocument.Index.name
        s = Search(index=INDEX_ALIAS).extra(track_total_hits=True)
        s = s.query("match_all")
        s = _parse_query_params(request, s)

        ordering = request.query_params.get("ordering", "").strip()
        field = ordering.lstrip("-")
        if field in SORTABLE:
            order = "desc" if ordering.startswith("-") else "asc"
            s = s.sort({field: {"order": order}}, "_score", {"id": "asc"})
        else:
            s = s.sort("_score", {"rating": "desc"}, {"id": "asc"})

        s = s[offset : offset + limit]

        try:
            response = s.execute()
        except Exception:
            logger.exception("Movie search failed")
            return Response({"error": "Search unavailable"}, status=503)

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
    try:
        logger.info("Getting produc details", extra={"movie_id": id})
        movie = Movies.objects.prefetch_related("cast", "language", "genre").get(id=id)
        serializer = MovieDetailSerializer(movie)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Movies.DoesNotExist:
        return Response({"data": "No such product"}, status=status.HTTP_404_NOT_FOUND)


def _csv(values):
    return [v.strip() for v in values.split(",") if v.strip()]


def _parse_query_params(request, s):
    params = request.query_params
    release_year = params.get("release_year", "").strip()
    if release_year:
        s = s.filter(
            "range",
            release_date={
                "gte": f"{release_year}-01-01",
                "lte": f"{release_year}-12-31",
            },
        )

    title = params.get("title", "").strip()
    if title:
        s = s.query("match", title={"query": title, "operator": "and"})

    # Genre filter
    genres = _csv(params.get("genre", ""))
    if genres:
        s = s.filter("terms", genre=genres)

    # language filter
    languages = _csv(params.get("language", ""))
    if languages:
        s = s.filter("terms", language=languages)

    # cast filter
    cast_list = _csv(params.get("cast", ""))
    if cast_list:

        def escape_wildcard(value: str) -> str:
            value = value.replace("\\", "\\\\").replace("*", "\\*").replace("?", "\\?")
            return value

        s = s.filter(
            Q(
                "bool",
                should=[
                    Q(
                        "wildcard",
                        cast={
                            "value": f"*{escape_wildcard(actor)}*",
                            "case_insensitive": True,
                        },
                    )
                    for actor in cast_list
                ],
            )
        )

    status = params.get("status", "")
    if status:
        s = s.filter("term", status=status)

    for name, op in (("rating", "gte"), ("price", "lte")):
        raw = params.get(name, "")
        if raw:
            try:
                s = s.filter("range", **{name: {op: float(raw)}})
            except ValueError:
                return Response(
                    {"error": f"Invalid {name} value"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
    return s
