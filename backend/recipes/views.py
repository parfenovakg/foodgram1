from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Recipe, Tag, Ingredient, Favorite, ShoppingCart
from .serializers import RecipeSerializer, TagSerializer, IngredientSerializer
from users.serializers import CustomUserSerializer

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_fields = ('name',)

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        return Response({'status': 'added to favorites'}, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def unfavorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        return Response({'status': 'added to shopping cart'}, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
