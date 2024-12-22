from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Item, Collection, CollectionItem
from PIL import Image
from decimal import Decimal, InvalidOperation
import numpy as np
from sklearn.cluster import KMeans
from userManager.models import Organization
from django.db import transaction
import logging

# Setup logging
logger = logging.getLogger(__name__)
@receiver(pre_save, sender=Item)
def calculate_discounted_price(sender, instance, **kwargs):
    """
    Calculate the discounted price before saving the Item.
    """
    try:
        discount_value = Decimal(instance.discount)
    except InvalidOperation:
        discount_value = Decimal('0.00')  # Default to 0 if invalid

    try:
        price_value = Decimal(instance.price)
    except InvalidOperation:
        price_value = Decimal('0.00')  # Default to 0 if invalid

    # Calculate discounted price
    if discount_value > 0:
        discount_amount = price_value * (discount_value / Decimal('100'))
        instance.discounted_price = price_value - discount_amount
    else:
        instance.discounted_price = price_value


@receiver(post_save, sender=Item)
def assign_cluster(sender, instance, **kwargs):
    """
     assign a price cluster after saving the Item.
    """

    # Assign price cluster if not already assigned
    if not instance._cluster_assigned:
        assign_price_cluster(instance)


def assign_price_cluster(item):
    """
    Dynamically assign the price cluster based on the item's price,
    but only for items with the same tag, category, and subject.
    """
    # Filter items by same tag, category, and subject
    similar_items = Item.objects.filter(
        tag=item.tag,
        category=item.category,
        subject=item.subject,
        grade=item.grade,
        curriculum=item.curriculum
    )
    if similar_items.count() >= 3:
        prices = np.array([float(item.price) for item in similar_items]).reshape(-1, 1)

        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=3)
        kmeans.fit(prices)
        clusters = kmeans.predict(prices)

        sorted_clusters = np.argsort(kmeans.cluster_centers_.flatten())
        cluster_labels = {
            sorted_clusters[0]: 'Economy Pack',
            sorted_clusters[1]: 'Value Pack',
            sorted_clusters[2]: 'Premium Pack'
        }

        # Assign cluster to similar items
        for similar_item, cluster in zip(similar_items, clusters):
            if not similar_item._cluster_assigned:
                similar_item.cluster = cluster_labels[cluster]
                similar_item._cluster_assigned = True
                similar_item.save()

        # Assign cluster to the current item
        item_cluster = kmeans.predict(np.array([[float(item.price)]]))[0]
        item.cluster = cluster_labels[item_cluster]
    else:
        # If less than 3 similar items, assign default cluster
        item.cluster = 'Economy Pack'

    # Set the flag to avoid recursion
    item._cluster_assigned = True
    item.save()
