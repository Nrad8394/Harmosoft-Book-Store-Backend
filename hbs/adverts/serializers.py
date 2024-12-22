from rest_framework import serializers
from .models import Advert

class AdvertSerializer(serializers.ModelSerializer):
    """
    Serializer for the Advert model.
    """

    class Meta:
        model = Advert
        fields = ['id', 'title', 'description', 'image', 'advert_type', 'organization', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
