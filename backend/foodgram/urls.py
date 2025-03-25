from django.contrib import admin
from django.urls import path, include
from recipes.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipes.urls')),  # Подключаем маршруты из приложения recipes
    path('auth/', include('djoser.urls')),  # Аутентификация djoser
    path('auth/', include('djoser.urls.jwt')),  # Авторизация через JWT
    path('', index, name='index'),
]
