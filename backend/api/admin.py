from django.contrib import admin

from django.contrib import admin
from .models import Ingredient, Tag, Recipe, IngredientAmount, Favorite, Cart


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "cooking_time")
    list_filter = ("tags",)
    search_fields = ("name", "author__username")


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "recipe", "amount")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")

