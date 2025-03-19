from django.urls import path, include
from rest_framework.routers import DefaultRouter
from recipes.views import IngredientViewSet, TagViewSet, RecipeViewSet

router = DefaultRouter()
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),  # Подключаем ViewSet через router
]
