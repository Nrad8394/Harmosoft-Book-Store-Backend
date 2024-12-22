from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Order, OrderItem, CancellationRequest, ReturnRequest, Receipt
from .serializers import OrderSerializer, OrderItemSerializer, CancellationRequestSerializer, ReturnRequestSerializer, ReceiptSerializer
from products.models import Item
from uuid import UUID
from rest_framework.permissions import AllowAny

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Extract the items from the request data
        items_data = request.data.pop('items', [])

        # Create the order
        order_serializer = self.get_serializer(data=request.data)
        order_serializer.is_valid(raise_exception=True)
        order = order_serializer.save()

        # Create the associated OrderItems
        for item_data in items_data:
            item_id = item_data.get('item_id')
            quantity = item_data.get('quantity', 1)

            try:
                # Fetch the item using the validated UUID
                item = Item.objects.get(sku=item_id)
            except Item.DoesNotExist:
                return Response({"error": f"Item with ID {item_id} not found."}, status=status.HTTP_400_BAD_REQUEST)
            OrderItem.objects.create(order=order, item=item, quantity=quantity)

        # Recalculate the total and save the order
        order.save()

        # Return the serialized order
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class CancellationRequestViewSet(viewsets.ModelViewSet):
    queryset = CancellationRequest.objects.all()
    serializer_class = CancellationRequestSerializer

class ReturnRequestViewSet(viewsets.ModelViewSet):
    queryset = ReturnRequest.objects.all()
    serializer_class = ReturnRequestSerializer

class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
