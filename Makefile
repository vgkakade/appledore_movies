
.PHONY: fixtures

serve:
	./manage.py runserver 8000

fixtures:
	./manage.py loaddata fixtures/actors.json
	./manage.py loaddata fixtures/genre.json
	./manage.py loaddata fixtures/language.json
	./manage.py loaddata fixtures/movies.json

superuser:
	./manage.py createsuperuser
