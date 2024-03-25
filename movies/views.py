from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter
from .models import Movie, Tag
from .serializers import MovieSerializer, RatingSerializer, TagSerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all().prefetch_related("tags").order_by("movielens_id")
    serializer_class = MovieSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ["title"]
    lookup_field = "movielens_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_query = self.request.query_params.get("genre", None)
        tag_query = self.request.query_params.get("tag", None)
        if genre_query:
            queryset = queryset.filter(genres__contains=[genre_query])
        if tag_query:
            queryset = queryset.filter(tags__text__icontains=tag_query)
        return queryset

    @action(
        detail=True,
        methods=["post"],
        url_path="rate",
        serializer_class=RatingSerializer,
    )
    def rate_movie(self, request, movielens_id=None):
        movie = self.get_object()
        user_id = request.data.get("userId")
        rating_value = request.data.get("rating")
        timestamp = request.data.get("timestamp")
        data = {
            "userId": user_id,
            "rating": rating_value,
            "timestamp": timestamp,
        }
        serializer = self.get_serializer(data=data, context={"movie": movie})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
