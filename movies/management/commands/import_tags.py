import csv
import logging
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from django.core.management.base import BaseCommand
from movies.models import Movie, Tag


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Import tags from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="Path to the CSV file containing tags",
        )

    def handle(self, *args, **options):
        csv_file_path = options["csv_file"]
        self.stdout.write(
            self.style.SUCCESS(f"Starting import of tags from {csv_file_path}")
        )
        self.import_tags(csv_file_path)
        self.stdout.write(self.style.SUCCESS("Import completed"))

    def import_tags(self, csv_file_path):
        rows_processed = 0
        entries_created = 0
        batch_size = 500000
        tags_batch = []

        with open(csv_file_path, "r") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows_processed += 1
                tag_data = self.process_tag(row)
                if tag_data:
                    tags_batch.append(tag_data)

                if rows_processed % batch_size == 0:
                    self.bulk_create_tags(tags_batch)
                    entries_created += len(tags_batch)
                    tags_batch = []
                    logger.info(f"Processed {rows_processed} rows.")

            if tags_batch:
                self.bulk_create_tags(tags_batch)
                entries_created += len(tags_batch)

        self.stdout.write(
            self.style.SUCCESS(
                f"Tags loaded successfully. Rows processed: {rows_processed}, Entries created: {entries_created}."
            )
        )

    def process_tag(self, row):
        movie_id = row["movieId"]
        movie = Movie.objects.filter(movielens_id=movie_id)
        if not movie.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Skipping tag for movie ID {movie_id}. Movie does not exist."
                )
            )
            return None
        movie = movie.first()
        return Tag(
            movielens_user_id=row["userId"],
            movie=movie,
            text=row["tag"],
            timestamp=timezone.make_aware(
                datetime.fromtimestamp(int(row["timestamp"])), timezone.utc
            ),
        )

    @transaction.atomic
    def bulk_create_tags(self, tags_batch):
        Tag.objects.bulk_create(tags_batch, ignore_conflicts=True)
