from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem, Order
from paymentsApp.models import Payment

@receiver(post_save, sender=OrderItem)
def update_order_total_on_save(sender, instance, **kwargs):
    """
    Update the total of the Order whenever an OrderItem is saved.
    Update the total discounted amount and total discount percentage as well.
    """
    order = instance.order
    order_items = order.items.all()

    total = 0
    total_discount_amount = 0
    total_original_price = 0

    # Calculate total, discount amount, and original price
    for order_item in order_items:
        item = order_item.item
        quantity = order_item.quantity

        item_total = item.discounted_price * quantity  # Using the discounted price
        total += item_total

        original_item_total = item.price * quantity
        discount_amount = original_item_total - item_total
        total_original_price += original_item_total
        total_discount_amount += discount_amount

    # Calculate discount percentage if there is any discount
    if total_original_price > 0:
        total_discount_percentage = (total_discount_amount / total_original_price) * 100
    else:
        total_discount_percentage = 0

    # Update the Order with the calculated totals
    order.total = total
    order.total_discount_amount = total_discount_amount
    order.total_discount_percentage = total_discount_percentage
    order.save()

    # Check if payment status needs to be updated
    update_payment_status(order)

@receiver(post_delete, sender=OrderItem)
def update_order_total_on_delete(sender, instance, **kwargs):
    """
    Update the total of the Order whenever an OrderItem is deleted.
    Update the total discounted amount and total discount percentage as well.
    """
    order = instance.order
    order_items = order.items.all()

    total = 0
    total_discount_amount = 0
    total_original_price = 0

    # Calculate total, discount amount, and original price
    for order_item in order_items:
        item = order_item.item
        quantity = order_item.quantity

        item_total = item.discounted_price * quantity  # Using the discounted price
        total += item_total

        original_item_total = item.price * quantity
        discount_amount = original_item_total - item_total
        total_original_price += original_item_total
        total_discount_amount += discount_amount

    # Calculate discount percentage if there is any discount
    if total_original_price > 0:
        total_discount_percentage = (total_discount_amount / total_original_price) * 100
    else:
        total_discount_percentage = 0

    # Update the Order with the calculated totals
    order.total = total
    order.total_discount_amount = total_discount_amount
    order.total_discount_percentage = total_discount_percentage
    order.save()

    # Check if payment status needs to be updated
    update_payment_status(order)

def update_payment_status(order):
    """
    Update the payment status of the Order to 'paid' if the amount_paid is equal to or exceeds the total.
    """
    if order.amount_paid >= order.total:
        order.payment_status = 'paid'
    else:
        order.payment_status = 'pending'
    order.save()

@receiver(post_save, sender=Payment)
def update_order_payment_on_payment(sender, instance, **kwargs):
    """
    Update the payment status of the Order whenever a Payment is saved.
    """
    order = instance.order
    update_payment_status(order)
