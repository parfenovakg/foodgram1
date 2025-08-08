from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import get_object_or_404, redirect
from django.urls import re_path

from recipes.models import Recipe
from django.views.generic import TemplateView


def short_redirect(request, code):
    recipe = get_object_or_404(Recipe, short_code=code)
    return redirect(f'/?recipe={recipe.id}')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:code>/', short_redirect, name='short-redirect'),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns += [
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
