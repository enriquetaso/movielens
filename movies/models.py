from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class GenreChoices(models.TextChoices):
    ACTION = "Action"
    ADVENTURE = "Adventure"
    ANIMATION = "Animation"
    CHILDRENS = "Children's"
    COMEDY = "Comedy"
    CRIME = "Crime"
    DOCUMENTARY = "Documentary"
    DRAMA = "Drama"
    FANTASY = "Fantasy"
    FILM_NOIR = "Film-Noir"
    HORROR = "Horror"
    MUSICAL = "Musical"
    MYSTERY = "Mystery"
    ROMANCE = "Romance"
    SCI_FI = "Sci-Fi"
    THRILLER = "Thriller"
    WAR = "War"
    WESTERN = "Western"
    NO_GENRE_LISTED = "(no genres listed)"


class Movie(models.Model):
    # The ID of movie should be UUID
    movielens_id = models.BigAutoField(primary_key=True, db_index=True)
    title = models.CharField(max_length=255)
    genres = ArrayField(
        models.CharField(max_length=20, choices=GenreChoices.choices),
    )

    def __str__(self):
        return f"{self.movielens_id}: {self.title}"


class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    # the user_id should be a foreign key to the User model
    movielens_user_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True, editable=True)

    class Meta:
        unique_together = ("movielens_user_id", "movie")

    def __str__(self):
        return f"{self.movielens_user_id} - {self.movie.title}: {self.rating}"


class Tag(models.Model):
    movielens_user_id = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="tags")
    text = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True, editable=True)

    class Meta:
        unique_together = ("movielens_user_id", "movie", "text")

    def __str__(self):
        return f"{self.movielens_user_id} - {self.movie.title}: {self.text}"
