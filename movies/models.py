from django.db import models


class Actor(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name


# Create your models here.
class Movies(models.Model):
    title = models.CharField(max_length=200, null=False, blank=False)
    release_date = models.DateField(null=True, blank=True)
    duration = models.PositiveIntegerField()
    genre = models.ManyToManyField(Genre, related_name="movies", blank=True)
    language = models.ManyToManyField(Language, related_name="movies")
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    poster = models.ImageField(upload_to="posters/")
    trailer_url = models.URLField(null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    cast = models.ManyToManyField(Actor, related_name="movies", blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
