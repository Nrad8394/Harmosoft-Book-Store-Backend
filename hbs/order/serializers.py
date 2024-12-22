from rest_framework import serializers
from .models import Order, OrderItem, CancellationRequest, ReturnRequest, Receipt
from order_tracking.models import OrderStep
from products.serializers import ItemSerializer
class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'
    def get_order_status(self, obj):
        # Get the latest completed step, or return None if no steps are completed
        latest_step = obj.steps.filter(completed=False).order_by('-timestamp').first()
        if latest_step:
            return latest_step.step_name
        return None  # Or return a default value like 'Pending' if no steps are completed
class CancellationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationRequest
        fields = '__all__'

class ReturnRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRequest
        fields = '__all__'

class ReceiptSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Receipt
        fields = '__all__'
        read_only_fields = ['order', 'timestamp']