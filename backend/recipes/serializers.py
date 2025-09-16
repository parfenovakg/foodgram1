from rest_framework import serializers
from django.db import transaction
from django.urls import reverse
from django.core.files.base import ContentFile
from django.db.models import Max, IntegerField
from django.db.models.functions import Cast
import base64
import imghdr

from .models import (Tag, Ingredient,
                     Recipe, RecipeIngredient,
                     Favorite, ShoppingCart)
from users.serializers import PublicUserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            header, b64 = data.split(';base64,')
            decoded = base64.b64decode(b64)
            ext = imghdr.what(None, decoded) or 'jpg'
            data = ContentFile(decoded, name=f'upload.{ext}')
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = PublicUserSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(
        source='recipe_ingredients', many=True
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    # short_link = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return bool(
            request and
            request.user.is_authenticated and
            Favorite.objects.filter(user=request.user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return bool(
            request and
            request.user.is_authenticated and
            ShoppingCart.objects.filter(user=request.user, recipe=obj).exists()
        )

class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'text', 'cooking_time',
                  'tags', 'ingredients')

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')

        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент.'
            })

        if len({item['ingredient'].id for
                item in ingredients}) != len(ingredients):
            raise serializers.ValidationError({
                'ingredients': 'Ингредиенты не должны повторяться.'
            })

        if not tags:
            raise serializers.ValidationError({
                'tags': 'Нужен хотя бы один тег.'
            })

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError({
                'tags': 'Теги не должны повторяться.'
            })

        return data

    @staticmethod
    def _set_m2m(recipe, tags, ingredients):
        recipe.tags.set(tags)
        objs = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['ingredient'],
                amount=item['amount']
            )
            for item in ingredients
        ]
        RecipeIngredient.objects.bulk_create(objs)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        last_code = (
            Recipe.objects
            .filter(short_code__regex=r'^\d+$')
            .annotate(code_int=Cast('short_code', IntegerField()))
            .aggregate(max_code=Max('code_int'))
            .get('max_code') or 0
        )
        next_code = str(last_code + 1).zfill(3)

        validated_data['short_code'] = next_code
        validated_data['author'] = self.context['request'].user

        recipe = Recipe.objects.create(**validated_data)
        self._set_m2m(recipe, tags, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        validated_data.pop('tags', None)
        validated_data.pop('ingredients', None)

        instance = super().update(instance, validated_data)

        return instance

    def to_representation(self, instance):
        return RecipeReadNoShortLinkSerializer(instance,
                                               context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('recipe',)

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = attrs['recipe']
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в избранном.')
        attrs['user'] = user
        return attrs

    def to_representation(self, instance):
        recipe = instance.recipe
        return {
            'id': recipe.id,
            'name': recipe.name,
            'image': self.context['request'].build_absolute_uri(
                recipe.image.url) if recipe.image else None,
            'cooking_time': recipe.cooking_time
        }


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('recipe',)

    def validate(self, attrs):
        user = self.context['request'].user
        recipe = attrs['recipe']
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в корзине.')
        attrs['user'] = user
        return attrs

    def to_representation(self, instance):
        recipe = instance.recipe
        return {
            'id': recipe.id,
            'name': recipe.name,
            'image': self.context['request'].build_absolute_uri(
                recipe.image.url)
            if recipe.image else None,
            'cooking_time': recipe.cooking_time
        }


class RecipeReadNoShortLinkSerializer(RecipeReadSerializer):
    class Meta(RecipeReadSerializer.Meta):
        fields = tuple(f for f in RecipeReadSerializer.Meta.fields
                       if f != 'short_link')
