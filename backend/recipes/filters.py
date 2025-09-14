import django_filters
from django_filters.rest_framework import filters

from .models import Recipe, Ingredient


class IngredientFilter(django_filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.CharFilter(method='filter_favorited')
    is_in_shopping_cart = filters.CharFilter(method='filter_in_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_favorited(self, qs, name, value):
        user = self.request.user
        if value == '1' and user.is_authenticated:
            return qs.filter(favorited_by__user=user)
        return qs

    def filter_in_cart(self, qs, name, value):
        user = self.request.user
        if value == '1' and user.is_authenticated:
            return qs.filter(in_shopping_cart__user=user)
        return qs
