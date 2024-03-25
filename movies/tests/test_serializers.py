import pytest
from movies.serializers import MovieSerializer, RatingSerializer


@pytest.mark.django_db
def test_movie_serializer_create():
    data = {"movieId": 16, "title": "Casino (1995)", "genres_list": "Crime|Drama"}
    serializer = MovieSerializer(data=data)
    assert serializer.is_valid()
    movie = serializer.save()
    assert movie.movielens_id == 16
    assert movie.title == "Casino (1995)"
    assert movie.genres == ["Crime", "Drama"]

    movie_data = MovieSerializer(movie).data
    assert movie_data == {
        "movieId": 16,
        "title": "Casino (1995)",
        "genres": "Crime|Drama",
        "tags": "",
        "average_rating": None,
        "link": "https://movielens.org/movies/16",
    }


@pytest.mark.django_db
def test_rating_serializer(movies):
    movie1, _ = movies
    data = {"userId": 1, "rating": 5.0}
    serializer = RatingSerializer(data=data, context={"movie": movie1})
    assert serializer.is_valid()
    rating = serializer.save()
    assert rating.movielens_user_id == 1
    assert rating.rating == 5.0

    rating_data = RatingSerializer(rating).data
    assert rating_data["userId"] == 1
    assert rating_data["rating"] == 5.0
