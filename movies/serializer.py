from rest_framework import serializers
from .models import Movies, Genre, Language, Actor


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name"]


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ["name"]


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ["name"]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movies
        fields = ["id", "title", "poster", "rating"]


class MovieDetailSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    cast = ActorSerializer(many=True)
    language = LanguageSerializer(many=True)

    class Meta:
        model = Movies
        fields = [
            "id",
            "title",
            "poster",
            "genre",
            "rating",
            "duration",
            "cast",
            "language",
            "description",
            "trailer_url",
        ]
