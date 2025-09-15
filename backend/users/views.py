from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import CustomUser, Follow
from .serializers import (
    CustomUserSerializer, FollowCreateSerializer,
    PublicUserSerializer, SubscriptionSerializer
)
from django.core.files.base import ContentFile
import base64
import imghdr


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
        model = CustomUser
        fields = ('avatar',)


class UserViewSet(DjoserUserViewSet):
    queryset = CustomUser.objects.all().order_by('id')
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return PublicUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = PublicUserSerializer(request.user,
                                          context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
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
        deleted_count, _ = Follow.objects.filter(user=request.user, author=author).delete()

        if deleted_count == 0:
            return Response(
                {'detail': 'Подписки не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


    # @action(detail=True, methods=['post', 'delete'],
    #         permission_classes=[IsAuthenticated])
    # def subscribe(self, request, id=None):
    #     author = self.get_object()
    #     if author == request.user:
    #         return Response({'detail': 'You cannot subscribe to yourself.'},
    #                         status=400)

    #     if request.method == 'POST':
    #         if Follow.objects.filter(user=request.user,
    #                                  author=author).exists():
    #             return Response({'detail':
    #                              'You are already subscribed to this user.'
    #                              }, status=400)

    #         Follow.objects.create(user=request.user, author=author)
    #         serializer = SubscriptionSerializer(
    #             author,
    #             context={'request': request}
    #         )
    #         return Response(serializer.data, status=201)
    #     if request.method == 'DELETE':
    #         follow_qs = Follow.objects.filter(user=request.user, author=author)
    #         if not follow_qs.exists():
    #             return Response(
    #                 {'detail': 'Подписки не существует'},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )
    #         follow_qs.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)

    #     Follow.objects.filter(user=request.user, author=author).delete()
    #     return Response(status=204)

    @action(detail=False, methods=['get'],
            permission_classes=[AllowAny])
    def subscriptions(self, request):
        authors = CustomUser.objects.filter(
            following__user=request.user).distinct()
        page = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    # @action(detail=False, methods=['patch', 'delete'],
    #         permission_classes=[IsAuthenticated], url_path='me/avatar')
    # def me_avatar(self, request):
    #     if request.method == 'DELETE':
    #         request.user.avatar.delete(save=True)
    #         return Response(status=204)
    #     ser = AvatarSerializer(request.user, data=request.data,
    #                            partial=True, context={'request': request})
    #     ser.is_valid(raise_exception=True)
    #     ser.save()
    #     return Response(CustomUserSerializer(request.user,
    #                                          context={'request': request}
    #                                          ).data)
