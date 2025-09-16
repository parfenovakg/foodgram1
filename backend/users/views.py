import base64
import imghdr

from django.core.files.base import ContentFile

from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet

from .models import User, Follow
from .serializers import (
    UserSerializer,
    FollowCreateSerializer,
    PublicUserSerializer,
    SubscriptionSerializer,
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            header, b64 = data.split(';base64,')
            decoded = base64.b64decode(b64)
            ext = imghdr.what(None, decoded) or 'jpg'
            data = ContentFile(decoded, name=f'upload.{ext}')
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
            return PublicUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
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

    @action(detail=False, methods=['get'],
            permission_classes=[AllowAny])
    def subscriptions(self, request):
        authors = User.objects.filter(
            following__user=request.user).distinct()
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
