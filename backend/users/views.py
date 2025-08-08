from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import CustomUser, Follow
from .serializers import CustomUserSerializer

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


class UserViewSet(viewsets.ModelViewSet): 
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        author = self.get_object()
        if author == request.user:
            return Response({'detail': 'Нельзя подписаться на себя.'}, status=400)
        if request.method == 'POST':
            Follow.objects.get_or_create(user=request.user, author=author)
            return Response(status=201)
        Follow.objects.filter(user=request.user, author=author).delete()
        return Response(status=204)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        authors = CustomUser.objects.filter(following__user=request.user).distinct()
        page = self.paginate_queryset(authors)
        ser = self.get_serializer(page, many=True, context={'request': request})
        return self.get_paginated_response(ser.data)

    @action(detail=False, methods=['patch', 'delete'], permission_classes=[IsAuthenticated], url_path='me/avatar')
    def me_avatar(self, request):
        if request.method == 'DELETE':
            request.user.avatar.delete(save=True)
            return Response(status=204)
        ser = AvatarSerializer(request.user, data=request.data, partial=True, context={'request': request})
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(CustomUserSerializer(request.user, context={'request': request}).data)