from rest_framework import serializers
from .models import Item, Collection, CollectionItem
from userManager.serializers import OrganizationSummarySerializer


class ItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the Item model.
    Converts Item instances to JSON and vice versa.
    
    Meta:
        model: The model being serialized (Item).
        fields: Specifies the fields to include in the serialization.
    """
    class Meta:
        model = Item
        fields = '__all__'


class CollectionItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the CollectionItem model. It connects the items and their quantities
    within a collection.
    
    item: A nested serializer for the item field, providing detailed item information.
    
    Meta:
        model: The model being serialized (CollectionItem).
        fields: Specifies the fields to include in the serialization.
    """
    item = ItemSerializer(read_only=True)  # Expecting the item's primary key (id)

    class Meta:
        model = CollectionItem
        fields = ['item', 'quantity', 'substitutable']  # Added substitutable field
class CollectionItemSerializerEditable(serializers.ModelSerializer):
    """
    Serializer for the CollectionItem model. It connects the items and their quantities
    within a collection.
    
    item: A nested serializer for the item field, providing detailed item information.
    
    Meta:
        model: The model being serialized (CollectionItem).
        fields: Specifies the fields to include in the serialization.
    """
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())  # Expecting the item's primary key (id)

    class Meta:
        model = CollectionItem
        fields = ['item', 'quantity', 'substitutable']  # Added substitutable field
class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Collection model. Includes related CollectionItem objects using
    the CollectionItemSerializer.
    
    items: A nested serializer that provides related items in the collection.
    
    Meta:
        model: The model being serialized (Collection).
        fields: Specifies the fields to include in the serialization.
    """
    items = CollectionItemSerializer(many=True)  # Nested serializer for collection items

    class Meta:
        model = Collection
        fields = '__all__'

    def create(self, validated_data):
        # Extract items data
        items_data = validated_data.pop('items', [])
        
        # Create the collection
        collection = Collection.objects.create(**validated_data)
        
        # Create collection items
        for item_data in items_data:
            CollectionItem.objects.create(collection=collection, **item_data)
        
        return collection

    def update(self, instance, validated_data):
        # Extract items data
        items_data = validated_data.pop('items', [])
        
        # Update the collection
        instance = super().update(instance, validated_data)
        
        # Clear existing items and add new ones
        instance.items.all().delete()
        for item_data in items_data:
            CollectionItem.objects.create(collection=instance, **item_data)
        
        return instance

class CollectionSummarySerializer(serializers.ModelSerializer):
    """
    Summary serializer for the Collection model, excluding related CollectionItem objects.
    This serializer is used for a lightweight representation of collections without item details.
    
    Meta:
        model: The model being serialized (Collection).
        fields: Specifies the fields to include in the serialization, excluding the items field.
    """
    school = OrganizationSummarySerializer(read_only=True)
    
    class Meta:
        model = Collection
        fields = ['id', 'name', 'school', 'grade']


class DynamicCollectionSerializer(serializers.Serializer):
    """
    Serializer for dynamically adjusting a collection based on a selected cluster.
    This will allow you to pass a modified collection without affecting the original.
    
    cluster_name: Name of the selected cluster (Economy Pack, Value Pack, Premium Pack).
    items: A nested serializer that provides access to the modified items in the collection.
    
    Meta:
        fields: The cluster name and the updated collection items.
    """
    cluster_name = serializers.CharField(max_length=20)
    items = CollectionItemSerializer(many=True, read_only=True)
    
    class Meta:
        fields = ['cluster_name', 'items']
