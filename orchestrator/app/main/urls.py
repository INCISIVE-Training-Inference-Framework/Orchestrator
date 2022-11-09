from django.urls import path, include
from rest_framework.routers import DefaultRouter

from main.api import views

router = DefaultRouter()
router.register(r'jobs', views.JobViewSet, basename='jobs')
urlpatterns = router.urls + [
    path('api-auth/', include('rest_framework.urls'))
]
