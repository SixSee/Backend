import django.http
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

from .settings import MEDIA_URL, MEDIA_ROOT, STATIC_ROOT, STATIC_URL


def home(request: django.http.HttpRequest):
    return HttpResponse(
        f"Api server running. <a href='{request.scheme}://{request.META['SERVER_NAME']}:{request.META['SERVER_PORT']}{request.path}swagger'>Swagger here!</a>")


schema_view = get_schema_view(
    openapi.Info(
        title="Excelegal admin apis",
        default_version='v1',
        description="Documentation of currently available apis",
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.authentication.urls')),
    path('', include('apps.courses.urls')),
    path('blog/', include('apps.blogs.urls')),
    path('quiz/', include('apps.quiz.urls')),
    path('bulletin/', include('apps.bulletin.urls')),
    path('classes/', include('apps.classes.urls')),
    path('internship/', include('apps.internship.urls')),
    path('', home, name="HOME")
]

urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += static(STATIC_URL, document_root=STATIC_ROOT)
