from django.contrib import admin

from .models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeIngredient,
    Favorite
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'favorites_count')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('tags',)

    inlines = [RecipeIngredientInline]

    def favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()
    favorites_count.short_description = 'Добавлений в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
