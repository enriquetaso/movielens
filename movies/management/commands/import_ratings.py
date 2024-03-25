# movies/management/commands/import_ratings.py
import csv
from datetime import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db import transaction
from movies.models import Movie, Rating


class Command(BaseCommand):
    help = "Import ratings from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file containing ratings",
        )

    def handle(self, *args, **options):
        start_time = timezone.now()
        csv_file_path = options["csv_file"]
        self.stdout.write(
            self.style.SUCCESS(f"Starting import of ratings from {csv_file_path}")
        )
        self.import_rating(csv_file_path)
        end_time = timezone.now()
        self.stdout.write(self.style.SUCCESS("Import completed"))
        elapsed_time = end_time - start_time
        self.stdout.write(self.style.SUCCESS(f"Total time taken: {elapsed_time}"))

    def import_rating(self, csv_file_path):
        rows_processed = 0
        entries_created = 0
        batch_size = 500000
        ratings_batch = []

        with open(csv_file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows_processed += 1
                rating_data = self.process_rating(row)
                if rating_data:
                    ratings_batch.append(rating_data)

                if rows_processed % batch_size == 0:
                    self.bulk_create_ratings(ratings_batch)
                    entries_created += len(ratings_batch)
                    ratings_batch = []

            if ratings_batch:
                self.bulk_create_ratings(ratings_batch)
                entries_created += len(ratings_batch)

        self.stdout.write(
            self.style.SUCCESS(
                f"Ratings loaded successfully. Rows processed: {rows_processed}, Entries created: {entries_created}."
            )
        )

    def process_rating(self, row):
        movie = Movie.objects.filter(movielens_id=row["movieId"])
        if not movie.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Skipping rating for movie ID {row['movieId']}. Movie does not exist."
                )
            )
            return None
        movie = movie.first()
        rating = Rating(
            movielens_user_id=row["userId"],
            movie=movie,
            rating=row["rating"],
            timestamp=timezone.make_aware(
                datetime.fromtimestamp(int(row["timestamp"])), timezone.utc
            ),
        )
        return rating

    @transaction.atomic
    def bulk_create_ratings(self, ratings_batch):
        Rating.objects.bulk_create(ratings_batch, ignore_conflicts=True)
