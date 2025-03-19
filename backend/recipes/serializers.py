from rest_framework import serializers
from .models import Ingredient, Tag, Recipe, RecipeIngredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name',
                  'image', 'text', 'ingredients',
                  'tags', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField()
    tags = serializers.ListField()

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time')
