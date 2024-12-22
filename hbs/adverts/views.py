from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Advert
from .serializers import AdvertSerializer

class AdvertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Advert objects.
    Supports all CRUD operations for adverts.
    """
    queryset = Advert.objects.all()
    serializer_class = AdvertSerializer
    permission_classes = [AllowAny]

    # def get_queryset(self):
    #     """
    #     Optionally filter adverts by the organization of the authenticated user.
    #     If the user is not authenticated, raise PermissionDenied.
    #     """
    #     user = self.request.user

    #     # Check if user is authenticated
    #     if  user.is_authenticated:
    #         # If the user is an organization, filter by their organization
    #         if user.user_type == 'organization':  # type: ignore
    #             return self.queryset.filter(organization=user)
        
    #     # Return all adverts for other  users (e.g., admin)
    #     return self.queryset
