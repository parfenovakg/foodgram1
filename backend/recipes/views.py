from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Recipe, Tag, Ingredient, Favorite, ShoppingCart
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer, FavoriteSerializer, ShoppingCartSerializer
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Recipe, Tag

class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Добавление и удаление рецепта из избранного."""
        recipe = self.get_object()
        if request.method == 'POST':
            Favorite.objects.get_or_create(user=request.user, recipe=recipe)
            return Response({'status': 'added to favorites'})
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response({'status': 'removed from favorites'})

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецепта из списка покупок."""
        recipe = self.get_object()
        if request.method == 'POST':
            ShoppingCart.objects.get_or_create(user=request.user, recipe=recipe)
            return Response({'status': 'added to shopping cart'})
        ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
        return Response({'status': 'removed from shopping cart'})

class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]

class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]


def index(request):
    """Главная страница с отображением рецептов и фильтрацией по тегам."""
    tag_filter = request.GET.getlist('tags')  # Получаем выбранные теги из URL
    recipes = Recipe.objects.all()

    if tag_filter:
        recipes = recipes.filter(tags__slug__in=tag_filter).distinct()

    paginator = Paginator(recipes, 6)  # Показываем по 6 рецептов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    tags = Tag.objects.all()
    return render(request, 'index.html', {'page_obj': page_obj, 'tags': tags})