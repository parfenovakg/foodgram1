from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Recipe, Tag, Ingredient, Favorite, ShoppingCart, RecipeIngredient
from .serializers import (
    RecipeReadSerializer, RecipeWriteSerializer,
    TagSerializer, IngredientSerializer, RecipeReadNoShortLinkSerializer
)
from .filters import RecipeFilter


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        u = request.user
        return u.is_authenticated and (obj.author == u or u.is_staff)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        
        if name:
            queryset = queryset.filter(name__icontains=name)
            
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'recipe_ingredients__ingredient'
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        if self.action in ('list', 'favorite', 'shopping_cart', 'retrieve'):
            return RecipeReadNoShortLinkSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data

        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Duplicate ingredients
        ids = [str(i.get('id') or i.get('ingredient')) for i in data.get('ingredients', [])]
        if len(ids) != len(set(ids)):
            return Response({'ingredients': 'Ingredients must not be duplicated'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Duplicate tags
        tags = data.get('tags') or []
        if len(tags) != len(set(tags)):
            return Response({'tags': 'Tags must not be duplicated'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Cooking time check
        if str(data.get('cooking_time')).isdigit() and int(data.get('cooking_time')) < 1:
            return Response({'cooking_time': 'Minimum cooking time is 1 minute'},
                            status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        data = request.data

        # Проверка ингредиентов до поиска рецепта
        if not data.get('ingredients'):
            return Response({'ingredients': 'At least one ingredient is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        ids = [str(i.get('id') or i.get('ingredient')) for i in data['ingredients']]
        if len(ids) != len(set(ids)):
            return Response({'ingredients': 'Ingredients must not be duplicated'},
                            status=status.HTTP_400_BAD_REQUEST)

        tags = data.get('tags') or []
        if len(tags) != len(set(tags)):
            return Response({'tags': 'Tags must not be duplicated'},
                            status=status.HTTP_400_BAD_REQUEST)

        if str(data.get('cooking_time')).isdigit() and int(data.get('cooking_time')) < 1:
            return Response({'cooking_time': 'Minimum cooking time is 1 minute'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Теперь проверка существования рецепта
        recipe = Recipe.objects.filter(pk=kwargs.get('pk')).first()
        if not recipe:
            return Response({'detail': 'Рецепта с таким ID не существует'},
                            status=status.HTTP_404_NOT_FOUND)

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        # Поведение идентично update
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = Recipe.objects.filter(pk=pk).first()
        if recipe is None:
            return Response({'errors': 'Recipe with this ID does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)
        if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
            return Response({'errors': 'Recipe is already in favorites'},
                            status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=request.user, recipe=recipe)
        data = {
            'id': recipe.id,
            'name': recipe.name,
            'image': request.build_absolute_uri(recipe.image.url) if recipe.image else None,
            'cooking_time': recipe.cooking_time
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if not favorite.exists():
            return Response({'errors': 'Recipe is not in favorites'},
                            status=status.HTTP_400_BAD_REQUEST)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = Recipe.objects.filter(pk=pk).first()
        if recipe is None:
            return Response({'errors': 'Recipe with this ID does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)
        if ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
            return Response({'errors': 'Recipe is already in shopping cart'},
                            status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        data = {
            'id': recipe.id,
            'name': recipe.name,
            'image': request.build_absolute_uri(recipe.image.url) if recipe.image else None,
            'cooking_time': recipe.cooking_time
        }
        return Response(data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        cart_item = ShoppingCart.objects.filter(user=request.user, recipe=recipe)
        if not cart_item.exists():
            return Response({'errors': 'Recipe is not in shopping cart'},
                            status=status.HTTP_400_BAD_REQUEST)
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        items = (
            RecipeIngredient.objects
            .filter(recipe__in_shopping_cart__user=request.user)
            .values(name=F('ingredient__name'),
                    unit=F('ingredient__measurement_unit'))
            .annotate(total=Sum('amount'))
            .order_by('name')
        )
        lines = [f"{i['name']} ({i['unit']}) — {i['total']}" for i in items]
        content = '\n'.join(lines) if lines else 'Список пуст.'

        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response
