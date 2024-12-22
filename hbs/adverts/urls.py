from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdvertViewSet

router = DefaultRouter()
router.register(r'adverts', AdvertViewSet, basename='advert')

urlpatterns = [
    path('', include(router.urls)),
]
