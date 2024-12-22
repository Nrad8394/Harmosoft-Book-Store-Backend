from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet, OrderStepViewSet, OrderChecklistViewSet, OrderItemChecklistViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
# router.register(r'trackorder', OrderStepViewSet)
router.register(r'orderchecklists', OrderChecklistViewSet)
router.register(r'order-item-checklists', OrderItemChecklistViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('trackorder/<str:pk>/', OrderStepViewSet.as_view({'get': 'list'})),  # Custom path to filter by order_id
]
