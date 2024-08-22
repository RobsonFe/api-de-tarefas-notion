from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API de Tarefa integrada com Notion",
        default_version='v1',
        description="API feita para gerenciar tarefas no AppWeb e sincronizar com Notion.",
        contact=openapi.Contact(email="robson-ferreiradasilva@hotmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/v1/', include('notion.urls')),
    path('docs/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('api/api.json', schema_view.without_ui(cache_timeout=0),
         name='schema-swagger-json'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
]
