# payments/models.py

from django.db import models
from order.models import Order
import uuid
from django.contrib.auth import get_user_model
User = get_user_model()

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='Customer', blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.CharField(max_length=50)
    result_code = models.CharField(max_length=100)
    result_desc = models.CharField(max_length=100)
    payment_status_choices = [
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
        ('incomplete', 'Incomplete'),
        ('paid', 'Paid'),
    ]
    payment_status = models.CharField(max_length=20, choices=payment_status_choices, blank=False, null=False, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id}"

class Refund(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_status = models.CharField(max_length=20, default='pending')
    refund_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund {self.id} for Payment {self.payment.id}"
