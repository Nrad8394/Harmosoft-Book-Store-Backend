from rest_framework import viewsets, status
from .models import Item, Collection, CollectionItem
from .serializers import ItemSerializer, CollectionSerializer, CollectionSummarySerializer, DynamicCollectionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from userManager.permissions import CustomUserPermission
from userManager.models import Organization
from rest_framework.exceptions import NotFound
from sklearn.cluster import KMeans
import numpy as np
from rest_framework.exceptions import ValidationError
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response

class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Item objects.
    Supports all CRUD operations for items in the collection.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='reassign-clusters')
    def reassign_clusters(self, request):
        """
        Custom action to reassign clusters for all items in the collection based
        on their tag, category, subject, grade, and curriculum.
        """
        try:
            # Retrieve all items to reassign clusters
            items = Item.objects.all()

            # Ensure there are items in the database
            if not items.exists():
                return Response({'detail': 'No items available to reassign clusters.'}, status=status.HTTP_404_NOT_FOUND)
            
            # Reassign clusters for each item
            for item in items:
                item.reassign_clusters()  # type: ignore # Call the method to reassign clusters

            return Response({'detail': 'Clusters reassigned successfully for all items.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [AllowAny]


    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Return collections without related items.
        """
        collections = self.queryset
        serializer = CollectionSummarySerializer(collections, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='school')
    def get_school_collections(self, request, pk=None):
        """
        Retrieve collections for the specified school.
        """
        school = self._get_school(pk)
        collections = Collection.objects.filter(school=school)
        serializer = CollectionSerializer(collections, many=True)
        return Response({
            'school_id': school.id,
            'school_name': school.organization_name,
            'collections': serializer.data
        })

    def _get_school(self, pk):
        """
        Retrieve a school by its primary key or raise an error if not found.
        """
        try:
            return Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            raise NotFound(detail="School not found.")

    @action(detail=True, methods=['post'], url_path='apply-cluster')
    def apply_cluster(self, request, pk=None):
        """
        Dynamically apply a price cluster (Economy, Value, Premium) to a collection without altering stored data.
        """
        collection = self.get_object()
        cluster_name = request.data.get('cluster_name')
        if not cluster_name:
            return Response({"error": "Cluster name is required"}, status=status.HTTP_400_BAD_REQUEST)

        updated_items = self._apply_price_cluster(collection, cluster_name)
        return Response({"cluster_name": cluster_name, "items": updated_items})

    def _apply_price_cluster(self, collection, cluster_name):
        """
        Apply a price cluster (Economy, Value, Premium) to the items in a collection.
        Items that are substitutable will be replaced according to the cluster logic.
        """
        items = collection.items.all()
        prices = np.array([item.item.price for item in items]).reshape(-1, 1)

        # Clustering using KMeans (dynamically adjust clusters if less than 3)
        num_clusters = min(3, len(items))
        kmeans = KMeans(n_clusters=num_clusters)
        kmeans.fit(prices)
        clusters = kmeans.predict(prices)

        cluster_map = {0: 'Economy Pack', 1: 'Value Pack', 2: 'Premium Pack'}
        selected_cluster = next(key for key, value in cluster_map.items() if value == cluster_name)

        modified_items = []
        for item, cluster in zip(items, clusters):
            if cluster == selected_cluster and item.substitutable:
                # If item is substitutable, replace with another item from the cluster
                alternative_item = self._get_alternative_item(item.item, cluster_name)
                if alternative_item:
                    modified_items.append({
                        'item': alternative_item,
                        'quantity': item.quantity
                    })
                else:
                    modified_items.append({
                        'item': item.item,
                        'quantity': item.quantity
                    })
            else:
                modified_items.append({
                    'item': item.item,
                    'quantity': item.quantity
                })

        # Serialize the items using the ItemSerializer
        serialized_items = [
            {"item": ItemSerializer(modified_item['item']).data, "quantity": modified_item['quantity']}
            for modified_item in modified_items
        ]
        
        return serialized_items

    def _get_alternative_item(self, item, cluster_name):
        """
        Retrieve an alternative item for substitution within the same category, subject, and tag.
        """
        return Item.objects.filter(
            category=item.category,
            subject=item.subject,
            tag=item.tag,
            price__lte=item.price
        ).exclude(pk=item.pk).first()
