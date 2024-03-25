# Movielens API

This API is a simple API that allows you to get information about movies and ratings from the Movielens 20 M dataset.

## Setup

To run this API, you need to have Python 3.9+, Docker and Docker Compose installed.

Build the Docker app image and db:

```bash
make docker/build
```

Run the Docker container:

```bash
make docker/migrate

make docker/run
```

Remove the Docker container:

```bash
make docker/stop
```

## Run tests:

```bash
make docker/tests
```

## Export movies:

 ```bash
 make docker/export_movie_links
 ```

## Endpoints

### Get all movies:

```bash
GET http://0.0.0.0:8000/api/movies/
```

### Retrieve single movie:

```bash
GET http://0.0.0.0:8000/api/movies/<movieId>/
```

### Rate a movie:

```bash
POST http://0.0.0.0:8000/api/movies/<movieId>/rate/
payload:
{
    "userId": 1,
    "rating": 5.0
}
```

### Ordering by title:

```bash
GET http://0.0.0.0:8000/api/movies/?ordering=title
```

### Filtering by tags:

```bash
GET http://0.0.0.0:8000/api/movies/?tags=japan
```

### Filtering by genre:

```bash
GET http://0.0.0.0:8000/api/movies/?genre=Action
```
