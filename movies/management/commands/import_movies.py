import csv
import logging
from django.core.management.base import BaseCommand
from movies.models import Movie, GenreChoices
from django.db import transaction


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load MovieLens ml-20m movies into the Movie model"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file containing movies",
        )

    def handle(self, *args, **options):
        csv_file_path = options["csv_file"]
        self.stdout.write(
            self.style.SUCCESS(f"Starting import of movies from {csv_file_path}")
        )
        self.import_movies(csv_file_path)
        self.stdout.write(self.style.SUCCESS("Import completed"))

    def import_movies(self, csv_file_path):
        rows_processed = 0
        entries_created = 0
        batch_size = 1000
        movies_batch = []

        with open(csv_file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows_processed += 1
                movie_data = self.import_movie(row)
                movies_batch.append(movie_data)

                if rows_processed % batch_size == 0:
                    self.bulk_create_movies(movies_batch)
                    entries_created += len(movies_batch)
                    movies_batch = []
                    logger.info(f"Processed {rows_processed} rows.")

            if movies_batch:
                self.bulk_create_movies(movies_batch)
                entries_created += len(movies_batch)

        self.stdout.write(
            self.style.SUCCESS(
                f"Movies loaded successfully. Rows processed: {rows_processed}, Entries created: {entries_created}."
            )
        )

    def import_movie(self, row):
        genres = row["genres"].split("|")
        # Filter valid genres based on GenreChoices
        genres = [genre for genre in genres if genre in GenreChoices.values]

        movie_data = {
            "movielens_id": row["movieId"],
            "title": row["title"],
            "genres": genres,
        }

        return movie_data

    @transaction.atomic
    def bulk_create_movies(self, movies_batch):
        movies_to_create = [Movie(**movie_data) for movie_data in movies_batch]
        Movie.objects.bulk_create(movies_to_create, ignore_conflicts=True)
