from django.contrib import admin
from .models import Actor, Genre, Language, Movies

# Register your models here.
admin.site.register(Actor)


class GenreAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


admin.site.register(Genre, GenreAdmin)


admin.site.register(Language)


class MoviesAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date", "duration", "price", "rating", "added_on")
    list_filter = ("release_date", "added_on", "language")
    sortable_by = ("title", "release_date", "price")
    # search_fields = ('title', 'description')


admin.site.register(Movies, MoviesAdmin)
