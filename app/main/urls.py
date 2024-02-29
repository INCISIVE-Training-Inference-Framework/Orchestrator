from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from main.api import views

router = DefaultRouter()
router.register(r'schemas', views.SchemaViewSet, basename='schemas')
router.register(r'executions', views.ExecutionViewSet, basename='executions')

urlpatterns = router.urls + [
    path('api-auth/', include('rest_framework.urls')),
    # SPECTACULAR URLS
    path('api/schemas/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schemas/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schemas'), name='swagger-ui'),
    path('api/schemas/redoc/', SpectacularRedocView.as_view(url_name='schemas'), name='redoc')
]
