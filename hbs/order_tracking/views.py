from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Order, OrderItem, OrderStep, OrderChecklist, OrderItemChecklist
from .serializers import OrderSerializer, OrderItemSerializer, OrderStepSerializer, OrderChecklistSerializer, OrderItemChecklistSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        order = self.get_object()
        item_data = request.data
        item_serializer = OrderItemSerializer(data=item_data)
        if item_serializer.is_valid():
            item_serializer.save(order=order)
            return Response(item_serializer.data)
        return Response(item_serializer.errors, status=400)

    @action(detail=True, methods=['post'])
    def add_step(self, request, pk=None):
        order = self.get_object()
        step_data = request.data
        step_serializer = OrderStepSerializer(data=step_data)
        if step_serializer.is_valid():
            step_serializer.save(order=order)
            return Response(step_serializer.data)
        return Response(step_serializer.errors, status=400)

    @action(detail=True, methods=['post'])
    def add_checklist(self, request, pk=None):
        order = self.get_object()
        checklist_data = request.data
        checklist_serializer = OrderChecklistSerializer(data=checklist_data)
        if checklist_serializer.is_valid():
            checklist_serializer.save(order=order)
            return Response(checklist_serializer.data)
        return Response(checklist_serializer.errors, status=400)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class OrderStepViewSet(viewsets.ModelViewSet):
    serializer_class = OrderStepSerializer
    queryset = OrderStep.objects.all()

    def get_queryset(self):
        """
        Filter the queryset by order_id, which is passed as part of the URL.
        """
        queryset = OrderStep.objects.all()
        order_id = self.kwargs.get('pk')  # Retrieve the order_id from the URL

        if order_id is not None:
            queryset = queryset.filter(order__id=order_id)

        return queryset

class OrderChecklistViewSet(viewsets.ModelViewSet):
    queryset = OrderChecklist.objects.all()
    serializer_class = OrderChecklistSerializer

class OrderItemChecklistViewSet(viewsets.ModelViewSet):
    queryset = OrderItemChecklist.objects.all()
    serializer_class = OrderItemChecklistSerializer
