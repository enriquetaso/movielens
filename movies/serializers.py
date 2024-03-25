from django.db.models import Avg
from rest_framework import serializers
from .models import Movie, GenreChoices, Rating, Tag


class TagSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source="movielens_user_id")
    movieId = serializers.IntegerField(source="movie.movielens_id")

    class Meta:
        model = Tag
        fields = ["text", "timestamp", "userId", "movieId"]

    def validate_movieId(self, value):
        if not Movie.objects.filter(movielens_id=value).exists():
            raise serializers.ValidationError("Movie not found.")
        return value

    def create(self, validated_data):
        movielens_id = validated_data.pop("movie")["movielens_id"]
        movie = Movie.objects.get(movielens_id=movielens_id)
        tag = Tag.objects.create(movie=movie, **validated_data)
        return tag


class MovieSerializer(serializers.ModelSerializer):
    movieId = serializers.IntegerField(source="movielens_id")
    genres = serializers.SerializerMethodField(method_name="get_genres_display")
    # tags can also be a nested field with TagSerializer(many=True, read_only=True)
    tags = serializers.SerializerMethodField()
    genres_list = serializers.CharField(write_only=True, required=False)
    average_rating = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = (
            "movieId",
            "title",
            "genres",
            "genres_list",
            "tags",
            "average_rating",
            "link",
        )

    def get_genres_display(self, obj):
        return "|".join(obj.genres)

    def get_tags(self, obj):
        # tags have been prefetched, this will not hit the database again
        tag_texts = list(set(obj.tags.all().values_list("text", flat=True)))
        return ", ".join(sorted(tag_texts))

    def get_average_rating(self, obj):
        average = Rating.objects.filter(movie=obj).aggregate(Avg("rating"))[
            "rating__avg"
        ]
        return round(average, 2) if average else None

    def get_link(self, obj):
        return f"https://movielens.org/movies/{obj.movielens_id}"

    def create(self, validated_data):
        genres_string = validated_data.pop("genres_list")
        genres_list = genres_string.split("|")
        genres = [genre for genre in genres_list if genre in GenreChoices.values]
        movie = Movie.objects.create(
            movielens_id=validated_data["movielens_id"],
            title=validated_data["title"],
            genres=genres,
        )
        return movie

    def update(self, instance, validated_data):
        genres_string = validated_data.pop("genres_list", None)
        if genres_string is not None:
            genres_list = genres_string.strip().replace('"', "").split("|")
            print(genres_list)
            genres = [genre for genre in genres_list if genre in GenreChoices.values]
            instance.genres = genres

        instance.title = validated_data.get("title", instance.title)
        instance.save()

        return instance


class RatingSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source="movielens_user_id")

    class Meta:
        model = Rating
        fields = ("userId", "rating", "timestamp")

    def validate(self, data):
        movie = self.context.get("movie")
        movielens_user_id = data.get("movielens_user_id")
        if Rating.objects.filter(
            movielens_user_id=movielens_user_id, movie=movie
        ).exists():
            raise serializers.ValidationError("You have already rated this movie.")
        return data

    def create(self, validated_data):
        movie = self.context.get("movie")
        if not movie:
            raise serializers.ValidationError("Movie not found.")
        return Rating.objects.create(movie=movie, **validated_data)
