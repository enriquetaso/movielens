VERSION=0.0.1
PYTHON_VERSION=3.12

format:
	black .

docker/build:
	docker compose build

docker/run:
	docker compose up -d

docker/stop:
	docker compose down

docker/remove:
	docker compose down -v

docker/makemigrations:
	docker compose run --rm app python manage.py makemigrations

docker/migrate:
	docker compose run --rm app python manage.py migrate

docker/tests:
	docker compose run --rm app pytest -v

docker/shell:
	docker compose run --rm app python manage.py shell_plus --print-sql --ipython

docker/show_urls:
	docker compose run --rm app python manage.py show_urls

docker/createsuperuser:
	docker compose run --rm app python manage.py createsuperuser

docker/admin_generator:
	docker compose run --rm app python manage.py admin_generator movies > movies/admin.py

###############
## Load data ##
###############

docker/import_movies:
	docker compose run --rm app python manage.py import_movies movies.csv

docker/import_ratings:
	docker compose run --rm app python manage.py import_ratings ratings.csv

docker/import_tags:
	docker compose run --rm app python manage.py import_tags tags.csv

docker/export_movie_links:
	docker compose run --rm app python manage.py export_movies -o output.csv