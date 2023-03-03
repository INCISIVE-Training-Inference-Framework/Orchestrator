from django.urls import path, include
from rest_framework.routers import DefaultRouter

from main.api import views

router = DefaultRouter()
router.register(r'schemas', views.SchemaViewSet, basename='schemas')
router.register(r'executions', views.ExecutionViewSet, basename='executions')

urlpatterns = router.urls + [
    path('api-auth/', include('rest_framework.urls'))
]
