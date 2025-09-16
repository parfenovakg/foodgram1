# from rest_framework import serializers

# from .models import User, Follow
# from recipes.models import Recipe


# class UserSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ('id', 'email', 'username',
#                   'first_name', 'last_name', 'avatar', 'is_subscribed')

#     def get_is_subscribed(self, obj):
#         request = self.context.get('request')
#         return bool(
#             request and
#             request.user.is_authenticated and
#             Follow.objects.filter(user=request.user, author=obj).exists()
#         )


# class RegisterUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("id", "username", "first_name", "last_name", "email")


# class PublicUserSerializer(serializers.ModelSerializer):
#     is_subscribed = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ("id", "username", "first_name",
#                   "last_name", "email", "is_subscribed")

#     def get_is_subscribed(self, obj):
#         request = self.context.get('request')
#         if not request or request.user.is_anonymous:
#             return False
#         return Follow.objects.filter(user=request.user, author=obj).exists()


# class RecipeMinSerializer(serializers.ModelSerializer):
#     """Simplified recipe serializer for subscription responses"""

#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'image', 'cooking_time')


# class SubscriptionSerializer(PublicUserSerializer):
#     """Serializer for user subscriptions with recipes"""
#     recipes_count = serializers.SerializerMethodField()
#     recipes = serializers.SerializerMethodField()

#     class Meta(PublicUserSerializer.Meta):
#         fields = PublicUserSerializer.Meta.fields + ('recipes_count',
#                                                      'recipes')

#     def get_recipes_count(self, obj):
#         return obj.recipes.count()

#     def get_recipes(self, obj):
#         request = self.context.get('request')
#         limit = request.query_params.get('recipes_limit')
#         recipes = obj.recipes.all()

#         if limit and limit.isdigit():
#             recipes = recipes[:int(limit)]

#         return RecipeMinSerializer(recipes, many=True).data


# class FollowCreateSerializer(serializers.ModelSerializer):
#     author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

#     class Meta:
#         model = Follow
#         fields = ('author',)

#     def validate(self, attrs):
#         user = self.context['request'].user
#         author = attrs['author']

#         if user == author:
#             raise serializers.ValidationError(
#                 'Нельзя подписаться на самого себя.')

#         if Follow.objects.filter(user=user, author=author).exists():
#             raise serializers.ValidationError(
#                 'Вы уже подписаны на этого пользователя.')

#         attrs['user'] = user
#         return attrs

#     def to_representation(self, instance):
#         return SubscriptionSerializer(instance.author,
#                                       context=self.context).data
