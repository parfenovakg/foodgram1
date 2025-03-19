from django.contrib import admin
from django.urls import path, include
from foodgram.views import index

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),  # Админка Django
    path('api/', include('api.urls')),  # Все API эндпоинты
    path('auth/', include('djoser.urls')),  # Регистрация и авторизация через Djoser
    path('auth/', include('djoser.urls.authtoken')),  # Авторизация через токены
]
