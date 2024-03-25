# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Movie, Rating, Tag


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("movielens_id", "title", "genres")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "movie",
        "rating",
        "movielens_user_id",
        "timestamp",
    )
    list_filter = ("timestamp",)
    raw_id_fields = ("movie",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "movielens_user_id", "movie", "text", "timestamp")
    list_filter = ("timestamp",)
    raw_id_fields = ("movie",)
