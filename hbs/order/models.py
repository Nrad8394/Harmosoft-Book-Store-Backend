from django.db import models
from products.models import Item
import uuid
from django.core.serializers import serialize
from django.db import models
from products.models import Item
import uuid
from userManager.models import Organization
import random
import string
from decimal import Decimal

def generate_unique_code():
    """Generate a unique 6-character alphanumeric code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
class Order(models.Model):
    id = models.CharField(primary_key=True, editable=False,max_length=6)
    date = models.DateField(auto_now_add=True)
    payment_status_choices = [
        ('pending', 'Pending'),
        ('refunded', 'Refunded'),
        ('failed', 'failed'),
        ('paid', 'Paid'),
    ]
    payment_status = models.CharField(max_length=20, choices=payment_status_choices, blank=False, null=False, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stripe_id = models.CharField(max_length=100, blank=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    mpesa_receipt_number = models.CharField(max_length=100, blank=True)
    receipient_name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, related_name='School', on_delete=models.CASCADE, blank=True, null=True)
    receipt_email = models.EmailField(max_length=100)
    delivered = models.BooleanField(default=False)
    GRADE_CHOICES = [
        ('ALL', 'ALL'),
        ('Play Group', 'Play Group'),
        ('Pre-Primary 1', "Pre-primary one"),
        ('Pre-Primary 2', 'Pre-primary two'),
        ('Grade 1', 'Grade One'),
        ('Grade 2', 'Grade Two'),
        ('Grade 3', 'Grade Three'),        
        ('Grade 4', "Grade Four"),
        ('Grade 5', 'Grade Five'),
        ('Grade 6', 'Grade Six'),
        ('Grade 7', 'Grade Seven'),
        ('Grade 8', "Grade Eight"),
        ('Grade 9', 'Grade Nine'),
        ('Grade 10', 'Grade Ten'),
        ('Grade 11', 'Grade Eleven'),
        ('Grade 12', 'Grade Twelve'),
    ]
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES,blank=True)
    total_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_discount_percentage = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    extra_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00')) # Packaging and Delivery fee
    def save(self, *args, **kwargs):
        # Ensure unique ID is generated before saving
        if not self.id:
            self.id = self.generate_unique_field('id')
        super(Order, self).save(*args, **kwargs)    
    def generate_unique_field(self, field_name):
        """Generate a unique 6-character alphanumeric code for a field."""
        code = generate_unique_code()
        while Order.objects.filter(**{field_name: code}).exists():
            code = generate_unique_code()
        return code
    def __str__(self):
        return f"Order {self.id} - {self.receipient_name}"
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def add_items(self, items):
        for item, quantity in items:
            OrderItem.objects.create(order=self, item=item, quantity=quantity)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

class CancellationRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    description = models.TextField()
    cancellation_status_choices = [
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('approved', 'Approved'),
    ]
    order_cancellation_status = models.CharField(max_length=20, choices=cancellation_status_choices, blank=False, null=False, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancellation request for {self.order}"

    class Meta:
        verbose_name = "Cancellation Request"
        verbose_name_plural = "Cancellation Requests"


class ReturnRequest(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    return_status_choices = [
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('approved', 'Approved'),
    ]
    return_status = models.CharField(max_length=20, choices=return_status_choices, blank=False, null=False, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return request for {self.order}"

    class Meta:
        verbose_name = "Return Request"
        verbose_name_plural = "Return Requests"
class Receipt(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt for order {self.order.id}"

    def get_order_details(self):
        """
        Returns the full order object with all associated items in JSON format.
        """
        # Accessing the order related items
        order_items = self.order.items.all()  # type: ignore # Retrieves all OrderItem instances related to the order
        
        # Serialize the order and its items
        order_data = serialize('json', [self.order], use_natural_primary_keys=True)
        order_items_data = serialize('json', order_items, use_natural_primary_keys=True)
        
        return {
            "order": order_data,
            "items": order_items_data,
        }

    class Meta:
        verbose_name = "Receipt"
        verbose_name_plural = "Receipts"

