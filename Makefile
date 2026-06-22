
.PHONY: fixtures

init:
	pip install -r requirements.txt
	pre-commit install
	./manage.py migrate
	./manage.py collectstatic --noinput
	./manage.py superuserexists || ./manage.py createsuperuser

serve:
	./manage.py runserver 8000

fixtures:
	./manage.py loaddata fixtures/actors.json
	./manage.py loaddata fixtures/genre.json
	./manage.py loaddata fixtures/language.json
	./manage.py loaddata fixtures/movies.json

superuser:
	./manage.py createsuperuser

celery:
	celery -A appledore_movies worker --loglevel=info

index_movies:
	./manage.py create_products_index
