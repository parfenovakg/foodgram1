import base64
import imghdr

from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from djoser.views import UserViewSet

from users.models import User, Follow
from recipes.models import (
    Recipe, Tag, Ingredient, Favorite, ShoppingCart, RecipeIngredient
)
from api.serializers import (
    UserSerializer, FollowCreateSerializer,
    SubscriptionSerializer,
    RecipeReadSerializer, RecipeWriteSerializer,
    ShoppingCartSerializer, TagSerializer,
    IngredientSerializer, FavoriteSerializer
)
from api.filters import RecipeFilter, IngredientFilter
from api.permissions import IsAuthorOrReadOnly


# ─────────────────────────────────────────────────────────────
#                         USERS
# ─────────────────────────────────────────────────────────────

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            header, b64 = data.split(';base64,')
            decoded = base64.b64decode(b64)
            ext = imghdr.what(None, decoded) or 'jpg'
            data = ContentFile(decoded, name=f'upload.{ext}')
        return super().to_internal_value(data)


class UserViewSet(UserViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
            return UserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        return super().me(request)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = self.get_object()
        serializer = FollowCreateSerializer(
            data={'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        author = self.get_object()
        deleted_count, _ = Follow.objects.filter(
            user=request.user, author=author).delete()
        if not deleted_count:
            return Response(
                {'detail': 'Подписки не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def subscriptions(self, request):
        authors = User.objects.filter(following__user=request.user).distinct()
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(page, many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)


# ─────────────────────────────────────────────────────────────
#                         TAGS
# ─────────────────────────────────────────────────────────────

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


# ─────────────────────────────────────────────────────────────
#                      INGREDIENTS
# ─────────────────────────────────────────────────────────────

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filterset_class = IngredientFilter


# ─────────────────────────────────────────────────────────────
#                         RECIPES
# ─────────────────────────────────────────────────────────────

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags', 'recipe_ingredients__ingredient'
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeWriteSerializer
        return RecipeReadSerializer

    # ──────── FAVORITES ────────

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        serializer = FavoriteSerializer(
            data={'recipe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted, _ = Favorite.objects.filter(user=request.user,
                                             recipe=recipe).delete()
        if not deleted:
            return Response(
                {'errors': 'Рецепт не был в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ──────── SHOPPING CART ────────

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        serializer = ShoppingCartSerializer(
            data={'recipe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        deleted, _ = ShoppingCart.objects.filter(user=request.user,
                                                 recipe=recipe).delete()
        if not deleted:
            return Response(
                {'errors': 'Рецепт не был в корзине'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ──────── DOWNLOAD CART ────────

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
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

        response = HttpResponse(content,
                                content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"')
        return response
