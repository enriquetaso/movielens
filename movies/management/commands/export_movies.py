from django.core.management.base import BaseCommand
from movies.models import Movie
import csv


class Command(BaseCommand):
    help = "Export movie list to CSV file including the MovieLens link"

    def add_arguments(self, parser):
        parser.add_argument(
            "-o",
            "--output",
            type=str,
            help="Path to output CSV file",
            default="movies_export.csv",
        )

    def handle(self, *args, **options):
        output_file_path = options["output"]
        self.stdout.write(
            self.style.SUCCESS(f"Starting export of movies to {output_file_path}")
        )
        headers = ["movieId", "title", "link"]

        with open(output_file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for movie in Movie.objects.all():
                link = f"https://movielens.org/movies/{movie.movielens_id}"
                writer.writerow([movie.movielens_id, movie.title, link])

        self.stdout.write(self.style.SUCCESS("Movies export completed successfully."))
