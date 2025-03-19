import django_filters
from .models import Recipe, Ingredient

class IngredientFilter(django_filters.FilterSet):
    """Фильтр для поиска ингредиентов по имени (по первым буквам)."""
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']

class RecipeFilter(django_filters.FilterSet):
    """Фильтр для рецептов по тегам и автору."""
    tags = django_filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')
    author = django_filters.CharFilter(field_name='author__username', lookup_expr='iexact')

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
