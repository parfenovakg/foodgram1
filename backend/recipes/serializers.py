from rest_framework import serializers
from .models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite, ShoppingCart
from django.contrib.auth import get_user_model

User = get_user_model()

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для связи рецепт-ингредиент (с указанием количества)."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']

class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    author = serializers.ReadOnlyField(source='author.username')
    ingredients = RecipeIngredientSerializer(many=True, source="recipeingredient_set")
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'name', 'image', 'text', 'ingredients', 'tags', 'cooking_time']

    def create(self, validated_data):
        """Создание рецепта с ингредиентами."""
        ingredients_data = validated_data.pop('recipeingredient_set')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient']['id'],
                amount=ingredient_data['amount']
            )

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        """Обновление рецепта с ингредиентами."""
        ingredients_data = validated_data.pop('recipeingredient_set')
        tags_data = validated_data.pop('tags')

        instance.ingredients.clear()
        instance.tags.clear()

        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_data['ingredient']['id'],
                amount=ingredient_data['amount']
            )

        instance.tags.set(tags_data)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()
        return instance

class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранных рецептов."""
    class Meta:
        model = Favorite
        fields = ['user', 'recipe']

class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""
    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']
