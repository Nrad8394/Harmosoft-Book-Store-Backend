from rest_framework import serializers
from .models import Order, OrderItem, OrderStep, OrderChecklist, OrderItemChecklist

class OrderItemChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemChecklist
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    item_checklists = OrderItemChecklistSerializer(many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderStepSerializer(serializers.ModelSerializer):
    step_name = serializers.CharField(source='get_step_name_display', read_only=True)
    class Meta:
        model = OrderStep
        fields = '__all__'

class OrderChecklistSerializer(serializers.ModelSerializer):
    item_checklists = OrderItemChecklistSerializer(many=True, read_only=True)

    class Meta:
        model = OrderChecklist
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    steps = OrderStepSerializer(many=True, read_only=True)
    checklists = OrderChecklistSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
