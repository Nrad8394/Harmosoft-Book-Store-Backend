# payments/admin.py

from django.contrib import admin
from .models import Payment, Refund

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'payment_method', 'payment_status', 'amount', 'transaction_id', 'created_at', 'updated_at')
    search_fields = ('order__id', 'payment_method', 'payment_status', 'transaction_id')
    list_filter = ('payment_method', 'payment_status', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'refund_amount', 'refund_status', 'refund_reason', 'created_at')
    search_fields = ('payment__id', 'refund_status')
    list_filter = ('refund_status', 'created_at')
    ordering = ('-created_at',)
