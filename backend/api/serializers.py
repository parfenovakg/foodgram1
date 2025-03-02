from rest_framework import serializers
from .models import Ingredient, Tag, Recipe, IngredientAmount


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "author", "image", "text", "tags", "ingredients", "cooking_time")

    def get_ingredients(self, obj):
        ingredients = IngredientAmount.objects.filter(recipe=obj)
        return [{"name": i.ingredient.name, "amount": i.amount, "unit": i.ingredient.measurement_unit} for i in ingredients]
