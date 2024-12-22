import nested_admin
from django.contrib import admin
from .models import OrderStep, OrderChecklist, OrderItemChecklist

class OrderItemChecklistInline(nested_admin.NestedTabularInline): # type: ignore
    model = OrderItemChecklist
    extra = 1

class OrderChecklistInline(nested_admin.NestedTabularInline): # type: ignore
    model = OrderChecklist
    extra = 1
    inlines = [OrderItemChecklistInline]  # Include OrderItemChecklists inline with OrderChecklists

class OrderStepAdmin(admin.ModelAdmin):
    list_display = ('order', 'step_name', 'completed', 'timestamp')
    list_filter = ('completed', 'timestamp', 'step_name')
    search_fields = ('order__id', 'step_name')
    ordering = ['timestamp']

class OrderChecklistAdmin(nested_admin.NestedModelAdmin): # type: ignore
    list_display = ('order', 'task', 'completed')
    list_filter = ('completed',)
    search_fields = ('order__id', 'task')
    inlines = [OrderItemChecklistInline]  # Include OrderItemChecklists inline with OrderChecklists

class OrderItemChecklistAdmin(admin.ModelAdmin):
    list_display = ('order_item', 'packaged', 'customer_confirmed')
    list_filter = ('packaged', 'customer_confirmed')
    search_fields = ('order_item__order__id', 'order_item__item__name')

# Register the admin classes
admin.site.register(OrderStep, OrderStepAdmin)
admin.site.register(OrderChecklist, OrderChecklistAdmin)
admin.site.register(OrderItemChecklist, OrderItemChecklistAdmin)
