from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import get_object_or_404, redirect

from recipes.models import Recipe


def short_redirect(request, code):
    recipe = get_object_or_404(Recipe, short_code=code)
    return redirect(f'/?recipe={recipe.id}')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:code>/', short_redirect, name='short-redirect'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
