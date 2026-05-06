def serialize_movie(movie):
    return {
        "id": movie.id,
        "title": movie.title,
        "description": movie.description,
        "release_date": movie.release_date.isoformat() if movie.release_date else None,
        "price": movie.price,
        "rating": movie.rating,
        "language": [lang.name for lang in movie.language.all()],
        "cast": [actor.name for actor in movie.cast.all()],
        "genre": [g.name for g in movie.genre.all()],
    }
