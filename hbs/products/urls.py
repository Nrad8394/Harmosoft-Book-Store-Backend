from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, CollectionViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'collections', CollectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
