from rest_framework import serializers
from django.db import transaction
from django.urls import reverse
from django.core.files.base import ContentFile
from django.db.models import Max
from django.db.models.functions import Cast
from django.db.models import IntegerField
import base64
import imghdr

from .models import Tag, Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart
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
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientInRecipeReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = PublicUserSerializer(read_only=True)
    ingredients = IngredientInRecipeReadSerializer(source='recipe_ingredients', many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    short_link = serializers.SerializerMethodField()
    

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time', 'short_link'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    def get_short_link(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(reverse('short-redirect', args=[obj.short_code]))
        return f'/s/{obj.short_code}'


class RecipeWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'text', 'cooking_time', 'tags', 'ingredients')

    def validate(self, data):
        if not data.get('ingredients'):
            raise serializers.ValidationError('Нужен хотя бы один ингредиент.')
        if not data.get('tags'):
            raise serializers.ValidationError('Нужен хотя бы один тег.')
        return data

    def _set_m2m(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        objs = [
            RecipeIngredient(recipe=recipe, ingredient=item['ingredient'], amount=item['amount'])
            for item in ingredients
        ]
        RecipeIngredient.objects.bulk_create(objs)

    # @transaction.atomic
    # def create(self, validated_data):
    #     tags = validated_data.pop('tags')
    #     ingredients = validated_data.pop('ingredients')
    #     #recipe = Recipe.objects.create(author=self.context['request'].user, **validated_data)
    #     recipe = Recipe.objects.create(**validated_data)
    #     self._set_m2m(recipe, tags, ingredients)
    #     return recipe

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        # Берём максимум только по тем short_code, что являются числами
        last_code = (
            Recipe.objects
            .filter(short_code__regex=r'^\d+$')              # только цифры
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
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.recipe_ingredients.all().delete()
            self._set_m2m(instance, instance.tags.all(), ingredients)
        return instance

    def to_representation(self, instance):
        return RecipeReadNoShortLinkSerializer(instance, context=self.context).data


    

class RecipeReadNoShortLinkSerializer(RecipeReadSerializer):
    class Meta(RecipeReadSerializer.Meta):
        fields = tuple(f for f in RecipeReadSerializer.Meta.fields if f != 'short_link')

