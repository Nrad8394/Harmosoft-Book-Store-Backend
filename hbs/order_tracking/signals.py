from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderStep,OrderChecklist,OrderItemChecklist
from paymentsApp.models import Payment
@receiver(post_save, sender=Payment)
def create_order_step_and_checklist_on_payment(sender, instance, created, **kwargs):
    """
    Create an OrderStep and OrderChecklist when a payment status changes to 'paid'.
    Ensure it only happens once for each order.
    """
    if instance.payment_status == 'paid':
        # Check if the 'completed' step has already been created for this order
        existing_step = OrderStep.objects.filter(order=instance.order).exists()
        existing_checklist = OrderChecklist.objects.filter(order=instance.order).exists()

        if not existing_step:
            # Create the 'Order Paid' step
            OrderStep.objects.create(
                order=instance.order,
                step_name='created',
                completed=False
            )

        if not existing_checklist:
            # Create the main checklist for the order
            order_checklist = OrderChecklist.objects.create(
                order=instance.order,
                task=f"Order{instance.order.id} Checklist",
                completed=False
            )

            # Automatically create OrderItemChecklist entries for each OrderItem in the order
            for order_item in instance.order.items.all():
                OrderItemChecklist.objects.create(
                    order_checklist=order_checklist,
                    order_item=order_item,
                    packaged=False,
                    customer_confirmed=False
                )

@receiver(post_save, sender=OrderStep)
def move_to_next_step(sender, instance, created, **kwargs):
    """
    Move the order to the next step when the current step is completed.
    """
    if instance.completed:
        # Define the order of steps
        step_order = [
            'created',
            'processing',
            'packaged',
            'shipped',
            'delivered',
            'completed'
        ]
        # Get the index of the current step
        current_step_index = step_order.index(instance.step_name)

        # If there is a next step, create it
        if current_step_index < len(step_order) - 1:
            next_step_name = step_order[current_step_index + 1]
            OrderStep.objects.create(
                order=instance.order,
                step_name=next_step_name
            )
