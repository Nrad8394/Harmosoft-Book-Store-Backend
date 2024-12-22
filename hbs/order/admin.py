from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.shortcuts import render
from .models import Order, OrderItem, CancellationRequest, ReturnRequest, Receipt
from django.utils.html import format_html

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'date',  'payment_status', 'total')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'item', 'quantity')

@admin.register(CancellationRequest)
class CancellationRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'order_cancellation_status', 'timestamp')

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'return_status', 'timestamp')

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('order', 'timestamp', 'view_order_details_link')
    search_fields = ('order', 'timestamp',)
    list_filter = ('timestamp',)

    def view_order_details_link(self, obj):
        """
        Return a link to the order details view in the admin interface.
        """
        url = f"{obj.id}/details/"
        return format_html('<a href="{}">View Details</a>', url)
    
    view_order_details_link.short_description = 'Order Details'

    def get_urls(self):
        """
        Add custom URL to view the order details.
        """
        urls = super().get_urls()
        custom_urls = [
            path('<int:receipt_id>/details/', self.admin_site.admin_view(self.order_details_view), name='order-details'),
        ]
        return custom_urls + urls

    def order_details_view(self, request, receipt_id):
        """
        Custom admin view to return the full order details as an HTML page.
        """
        receipt = self.get_object(request, receipt_id)
        if not receipt:
            return JsonResponse({'error': 'Receipt not found'}, status=404)

        context = dict(
            self.admin_site.each_context(request),
            receipt=receipt,
        )

        return render(request, "admin/order/receipt_order_details.html", context)
