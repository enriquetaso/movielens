import pytest
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse
from rest_framework.test import APIClient
from movies.models import Movie, Rating, Tag


@pytest.mark.django_db
def test_movie_list_view(client, movies):
    movie1, _ = movies
    response = client.get("/api/movies/")
    assert response.status_code == 200
    assert len(response.data["results"]) == 2
    assert response.data["results"][0]["movieId"] == movie1.movielens_id


@pytest.mark.django_db
def test_movie_genre_filter_view(client, movies):
    response = client.get("/api/movies/?genre=Comedy")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_movie_tag_filter_view_null(client, movies, tag):
    response = client.get(f"/api/movies/?tag=empty")
    assert response.status_code == 200
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_movie_tag_filter_view(client, movies, tag):
    tag, _, _ = tag
    response = client.get(f"/api/movies/?tag={tag.text}")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_movie_ordering_view(client, movies):
    response = client.get("/api/movies/?ordering=title")
    assert response.status_code == 200
    assert len(response.data["results"]) == 2


@pytest.mark.django_db
def test_movie_detail_view(client, movies):
    movie1, _ = movies
    response = client.get(f"/api/movies/{movie1.movielens_id}/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_movie_detail_view_not_found(client):
    response = client.get("/api/movies/99999/")
    assert response.status_code == 404
    assert response.data == {"detail": "Not found."}


@pytest.mark.django_db
def test_movie_update_view(client, user, movies):
    movie, _ = movies
    client.force_login(user)

    url = f"/api/movies/{movie.movielens_id}/"
    payload = {
        "movieId": movie.movielens_id,
        "title": "New Title",
        "genres_list": "Action|Drama",
    }
    response = client.put(url, payload, content_type="application/json")

    assert response.status_code == 200
    assert response.data["movieId"] == 1
    assert response.data["title"] == "New Title"
    assert response.data["genres"] == "Action|Drama"

    movie.refresh_from_db()
    assert movie.title == "New Title"
    assert movie.genres == ["Action", "Drama"]
    client.logout()


@pytest.mark.django_db
def test_movie_delete_view(client, user, movies):
    client.force_login(user)
    movie, _ = movies
    url = f"/api/movies/{movie.movielens_id}/"
    response = client.delete(url)
    assert response.status_code == 204

    response = client.get(url)
    assert response.status_code == 404
    client.logout()


@pytest.mark.django_db
def test_movie_create_view():
    User.objects.create_user(username="testuser", password="password")
    client = APIClient()
    client.login(username="testuser", password="password")

    response = client.post(
        "/api/movies/",
        {"movieId": 1, "title": "Test Movie (1995)", "genres_list": "Action|Comedy"},
    )
    assert response.status_code == 201
    assert response.data["movieId"] == 1
    assert response.data["title"] == "Test Movie (1995)"
    assert response.data["genres"] == "Action|Comedy"

    movie = Movie.objects.get(movielens_id=1)
    assert movie.title == "Test Movie (1995)"
    assert movie.genres == ["Action", "Comedy"]

    client.logout()


@pytest.mark.django_db
def test_movie_partial_update_view(client, user, movies):
    client.force_login(user)

    movie, _ = movies
    url = f"/api/movies/{movie.movielens_id}/"
    payload = {"title": "New Title"}
    response = client.patch(url, payload, content_type="application/json")
    assert response.status_code == 200
    assert response.data["title"] == "New Title"

    movie.refresh_from_db()
    assert movie.title == "New Title"
    assert movie.genres == ["Action", "Comedy"]
    client.logout()


@pytest.mark.django_db
def test_create_rating(client, user, movies):
    movie, _ = movies
    client.force_login(user=user)

    movielens_user_id = 1
    url = reverse("movie-rate-movie", kwargs={"movielens_id": movie.movielens_id})
    data = {
        "userId": movielens_user_id,
        "rating": 3.0,
        "timestamp": "2006-05-17T12:27:08Z",
    }

    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Rating.objects.count() == 1

    # Attempt to create a duplicate rating
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_tag(client, user, movies):
    client.force_login(user=user)
    url = reverse("tag-list")

    movie, _ = movies
    movielens_user_id = 1
    data = {
        "userId": movielens_user_id,
        "movieId": movie.movielens_id,
        "text": "Test Tag",
        "timestamp": "2006-05-17T12:27:08Z",
    }

    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
