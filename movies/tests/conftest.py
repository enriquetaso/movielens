import pytest
from django.contrib.auth.models import User
from movies.models import Movie, Tag


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="12345")


@pytest.fixture
def movies(db):
    movie1 = Movie.objects.create(
        movielens_id=1, title="Test Movie (1995)", genres=["Action", "Comedy"]
    )
    movie2 = Movie.objects.create(
        movielens_id=2, title="Test Movie 2 (1996)", genres=["Action", "Drama"]
    )
    return movie1, movie2


@pytest.fixture
def tag(db):
    user = User.objects.create_user(username="testuser", password="12345")
    movie = Movie.objects.create(
        movielens_id=3, title="Test Movie (2005)", genres=["Action", "Comedy"]
    )
    tag = Tag.objects.create(movie=movie, movielens_user_id=user.id, text="Test Tag")
    return tag, movie, user
