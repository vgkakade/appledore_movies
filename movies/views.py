from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination

from elasticsearch_dsl import Search, Q

from .serializer import MovieSerializer, MovieDetailSerializer
from .models import Movies


# Create your views here.
class MovieSearchView(APIView):
    pagination_class = LimitOffsetPagination

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        genre = request.query_params.get("genre", "").strip()
        rating_gte = request.query_params.get(
            "rating__gte", ""
        ).strip()  # fixed param name
        ordering = request.query_params.get("ordering", "-rating")

        # Start fresh every time
        s = Search(index="movies").extra(track_total_hits=True)

        # Default: show all if no filters/search
        has_filter = bool(query or genre or rating_gte)
        if has_filter:
            # We will add queries/filters below
            pass
        else:
            s = s.query("match_all")

        # Full-text search
        if query:
            from elasticsearch_dsl import Q  # import here or at top

            s = s.query(
                Q(
                    "multi_match",
                    query=query,
                    fields=[
                        "title^5",
                        "description^1",
                        "cast.name^3",
                        "genre.name^2",
                        "language.name^1",
                    ],
                    fuzziness="AUTO",
                    type="best_fields",
                )
            )

        # Genre filter (exact)
        if genre:
            s = s.filter("term", **{"genre.name.raw": genre.title()})

        # Rating filter
        if rating_gte:
            try:
                s = s.filter("range", rating={"gte": float(rating_gte)})
            except ValueError:
                pass  # ignore invalid number

        # Sorting — always apply (fallback to _score if field invalid)
        sort_field = ordering.lstrip("-")
        sort_order = "desc" if ordering.startswith("-") else "asc"
        s = s.sort(
            {sort_field: {"order": sort_order}}, "_score"
        )  # _score as tie-breaker

        # Pagination — fixed slice syntax
        limit = int(request.query_params.get("limit", 20))
        offset = int(request.query_params.get("offset", 0))
        s = s[offset : offset + limit]

        # Execute
        response = s.execute()

        # Fallback if zero hits (e.g., invalid sort field)
        if len(response.hits) == 0 and has_filter:
            # Retry without query but with default sort
            s = (
                Search(index="movies")
                .sort("-rating", "_score")[offset : offset + limit]
                .extra(track_total_hits=True)
            )
            response = s.execute()

        # Extract IDs safely
        movie_ids = []
        for hit in response.hits:
            if hasattr(hit.meta, "id"):
                try:
                    movie_ids.append(int(hit.meta.id))
                except:
                    pass

        if not movie_ids:
            return Response({"count": 0, "results": []})

        # Fetch Django objects and preserve ES order
        movies_qs = Movies.objects.filter(id__in=movie_ids)
        movie_dict = {m.id: m for m in movies_qs}
        ordered_movies = [movie_dict[mid] for mid in movie_ids if mid in movie_dict]

        serializer = MovieSerializer(ordered_movies, many=True)

        total_count = (
            response.hits.total.value
            if hasattr(response.hits.total, "value")
            else len(response.hits)
        )

        return Response({"count": total_count, "results": serializer.data})


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
