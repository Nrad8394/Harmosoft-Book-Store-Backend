from django.shortcuts import render, redirect
from django.urls import reverse
from allauth.account.models import EmailConfirmationHMAC, EmailConfirmation
from rest_framework import viewsets, status
from .models import CustomUser, Individual, Organization, Admin
from .serializers import (
    CustomUserSerializer, IndividualSerializer, 
    OrganizationSerializer, AdminSerializer,
    IndividualSummarySerializer,OrganizationSummarySerializer,
    AdminSummarySerializer,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import CustomUserPermission
from rest_framework.response import Response
from rest_framework.decorators import action

def confirm_email(request, key):
    """
    View to handle email confirmation from a unique key.
    
    If the key is valid and the confirmation is successful,
    the user is redirected to the 'email_confirmation_done' page.
    """
    try:
        confirmation = EmailConfirmationHMAC.from_key(key)
        if confirmation:
            confirmation.confirm(request)
            return redirect(reverse('email_confirmation_done'))
    except EmailConfirmation.DoesNotExist:
        pass

    return render(request, 'account/confirm_email.html', {'key': key})

def email_confirmation_done(request):
    """
    View to render a success page after email confirmation.
    """
    return render(request, 'account/email_confirmation_done.html')


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    API viewset for viewing and editing CustomUser instances.
    
    Provides GET, HEAD, and OPTIONS methods.
    Users can view their own information.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [CustomUserPermission]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ['get', 'head', 'options']

    def get_object(self):
        """
        Returns the CustomUser object of the currently authenticated user.
        """
        return CustomUser.objects.get(id=self.request.user.id)


class IndividualViewSet(viewsets.ModelViewSet):
    """
    API viewset for viewing and editing Individual instances.
    
    Provides methods to retrieve and update individual user details.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']  # Include PATCH method

    def get_queryset(self):
        """
        Filters the Individual queryset to the currently authenticated user.
        """
        return Individual.objects.filter(id=self.request.user.id)

    def get_object(self):
        """
        Returns the Individual object of the currently authenticated user.
        """
        return Individual.objects.get(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        """
        Updates the individual instance for the authenticated user.
        """
        individual = self.get_object()
        serializer = self.get_serializer(individual, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates the individual instance for the authenticated user.
        """
        individual = self.get_object()
        serializer = self.get_serializer(individual, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Custom endpoint to return individuals without the related items.
        """
        individuals = Individual.objects.all()
        serializer = IndividualSummarySerializer(individuals, many=True)
        return Response(serializer.data)

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API viewset for viewing and editing Organization instances.
    
    Provides methods to retrieve and update organization user details.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [CustomUserPermission]
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']  # Include PATCH method

    def get_queryset(self):
        """
        Filters the Organization queryset to the currently authenticated user.
        """
        return Organization.objects.filter(id=self.request.user.id)

    def get_object(self):
        """
        Returns the Organization object of the currently authenticated user.
        """
        return Organization.objects.get(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        """
        Updates the organization instance for the authenticated user.
        """
        organization = self.get_object()
        serializer = self.get_serializer(organization, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates the organization instance for the authenticated user.
        """
        organization = self.get_object()
        serializer = self.get_serializer(organization, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Custom endpoint to return organizations without the related items.
        """
        organizations = Organization.objects.all()
        serializer = OrganizationSummarySerializer(organizations, many=True)
        return Response(serializer.data)
class AdminViewSet(viewsets.ModelViewSet):
    """
    API viewset for viewing and editing Admin instances.
    
    Provides methods to retrieve and update admin user details.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [CustomUserPermission]
    queryset = Admin.objects.all()
    serializer_class = AdminSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']  # Include PATCH method

    def get_queryset(self):
        """
        Filters the Admin queryset to the currently authenticated user.
        """
        return Admin.objects.filter(id=self.request.user.id)

    def get_object(self):
        """
        Returns the Admin object of the currently authenticated user.
        """
        return Admin.objects.get(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        """
        Updates the admin instance for the authenticated user.
        """
        admin = self.get_object()
        serializer = self.get_serializer(admin, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates the admin instance for the authenticated user.
        """
        admin = self.get_object()
        serializer = self.get_serializer(admin, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Custom endpoint to return admins without the related items.
        """
        admins = Admin.objects.all()
        serializer = AdminSummarySerializer(admins, many=True)
        return Response(serializer.data)
