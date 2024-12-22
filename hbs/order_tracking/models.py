from django.db import models
from products.models import Item
from order.models import Order, OrderItem

class OrderStep(models.Model):
    STEP_CHOICES = [
        ('created', 'Order Created'),
        ('processing', 'Processing'),
        ('packaged', 'Packaged'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
    ]
    
    order = models.ForeignKey(Order, related_name='steps', on_delete=models.CASCADE)
    step_name = models.CharField(max_length=100, choices=STEP_CHOICES)
    completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.step_name}"

    def complete_step(self):
        """
        Marks the current step as completed and saves the model.
        """
        self.completed = True
        self.save()

    class Meta:
        verbose_name = "Order Step"
        verbose_name_plural = "Order Steps"
        ordering = ['timestamp']  # Ensure steps are ordered by when they were created


class OrderChecklist(models.Model):
    order = models.ForeignKey(Order, related_name='checklists', on_delete=models.CASCADE)
    task = models.CharField(max_length=100)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Task: {self.task} - {'Completed' if self.completed else 'Pending'}"

    def check_all_tasks_completed(self):
        """
        Checks if all tasks in the checklist and all item-specific tasks in the checklist are completed.
        """
        item_checklists = self.item_checklists.all()  # type: ignore # Retrieve related item checklists
        
        # Ensure there are item checklists to evaluate
        if not item_checklists.exists():
            return False
        
        all_items_completed = all(item_checklist.is_completed() for item_checklist in item_checklists)
        
        return self.completed and all_items_completed
    def save(self, *args, **kwargs):
        # Save the checklist first
        super(OrderChecklist, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Order Checklist"
        verbose_name_plural = "Order Checklists"


class OrderItemChecklist(models.Model):
    order_checklist = models.ForeignKey(OrderChecklist, related_name='item_checklists', on_delete=models.CASCADE)
    order_item = models.ForeignKey(OrderItem, related_name='item_checklists', on_delete=models.CASCADE)
    packaged = models.BooleanField(default=False)
    customer_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Item: {self.order_item.item.name} - {'Packaged' if self.packaged else 'Not Packaged'}, {'Confirmed' if self.customer_confirmed else 'Not Confirmed'}"

    def is_completed(self):
        """
        Checks if the item-specific checklist is completed.
        """
        return self.packaged and self.customer_confirmed

    class Meta:
        verbose_name = "Order Item Checklist"
        verbose_name_plural = "Order Item Checklists"
