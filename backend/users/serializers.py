from rest_framework import serializers
from django.db.models import Count
from .models import CustomUser, Follow
from recipes.models import Recipe


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'avatar', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "first_name", "last_name", "email")

class PublicUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ("id", "username", "first_name", "last_name", "email", "is_subscribed")

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(user=request.user, author=obj).exists()


class RecipeMinSerializer(serializers.ModelSerializer):
    """Simplified recipe serializer for subscription responses"""
    
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')



class SubscriptionSerializer(CustomUserSerializer):
    """Serializer for user subscriptions with recipes"""
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    
    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes_count', 'recipes')
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()
    
    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
            
        return RecipeMinSerializer(recipes, many=True).data
