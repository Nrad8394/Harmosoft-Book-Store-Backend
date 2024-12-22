from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import setup_user_email
from allauth.account import app_settings as allauth_account_settings
from django.utils.translation import gettext_lazy as _
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import CustomUser, Individual, Organization, Admin
from paymentsApp.models import Payment
from products.models import Collection

User = get_user_model()

class CustomRegisterSerializer(RegisterSerializer):
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES) # type: ignore
    admin_code = serializers.CharField(required=False, allow_blank=True)
    parent_organization_id = serializers.IntegerField(required=False)
    organization_name = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    def get_cleaned_data(self):
        """
        Overrides the method to include additional fields from the request data.
        """
        data = super().get_cleaned_data()
        data['user_type'] = self.validated_data.get('user_type', '') if self.validated_data else '' # type: ignore
        data['email'] = self.validated_data.get('email', '') if self.validated_data else ''# type: ignore
        data['username'] = self.validated_data.get('username', self.generate_username_from_email(data['email']))  # type: ignore # Generate username if not provided
        return data

    def generate_username_from_email(self, email):
        """
        Generate a username based on the email if the username is not provided.
        """
        return email.split('@')[0]

    def validate_email(self, email):
        """
        Check if the email already exists.
        """
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return email

    def save(self, request):
        """
        Overrides the save method to handle custom user type creation using request data.
        """
        adapter = get_adapter()
        self.cleaned_data = self.get_cleaned_data()

        # Retrieve additional fields directly from the request
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        organization_name = request.data.get('organization_name', '')
        location = request.data.get('location', '')
        level = request.data.get('level', '')
        curriculum = request.data.get('curriculum', '')
        address = request.data.get('address', '')
        
        # print("Request Data:", request.data)
        # print("Cleaned Data:", self.cleaned_data)

        # Validate email before proceeding
        self.validate_email(self.cleaned_data['email'])

        # Start transaction block to ensure atomicity
        with transaction.atomic():
            user_type = self.cleaned_data['user_type']
            username = self.cleaned_data['username']
            email = self.cleaned_data['email']

            if user_type == 'individual':
                user = Individual.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    date_of_birth=None,  # Add any other Individual-specific fields here
                )
            elif user_type == 'organization':
                organization_name = organization_name or first_name  # Ensure organization_name is set
                user = Organization.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    organization_name=organization_name,
                    address=address,
                    verified=False,
                    location=location,
                    level=level,
                    curriculum=curriculum,
                )
            elif user_type == 'admin':
                user = Admin.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    is_superuser=True,
                    is_staff=True,
                    is_admin=True,
                )

            # Finalize the user creation using the adapter
            user = adapter.save_user(request, user, self, commit=False)
            user.user_type = user_type
            user.save()

            self.custom_signup(request, user)
            setup_user_email(request, user, [])

            return user
class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model.

    Attributes:
        email_verified (SerializerMethodField): Field to check if the user's email is verified.
    """
    email_verified = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'required': False, 'write_only': True},
        }

    def get_email_verified(self, obj):
        """
        Check if the user's primary email is verified.

        Args:
            obj (CustomUser): The user object.

        Returns:
            bool: True if the email is verified, otherwise False.
        """
        try:
            email_address = EmailAddress.objects.get(user=obj, primary=True)
            return email_address.verified
        except EmailAddress.DoesNotExist:
            return False
from order.models import OrderItem,Order
from products.models import Item
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
class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()  # This will serialize the entire item object, not just the ID.

    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'item']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'
    def get_order_status(self, obj):
        # Get the latest completed step, or return None if no steps are completed
        latest_step = obj.steps.filter(completed=False).order_by('-timestamp').first()
        if latest_step:
            return latest_step.step_name
        return None  # Or return a default value like 'Pending' if no steps are completed
class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Payment model.
    """
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_method', 'payment_status', 'amount', 'transaction_id', 'created_at']

class IndividualSerializer(serializers.ModelSerializer):
    """
    Serializer for the Individual model, including associated payments.
    """
    payments = PaymentSerializer(many=True, read_only=True, source='Customer')

    class Meta:
        model = Individual
        fields = '__all__'
        extra_kwargs = {
                    'username': {'required': False},
                    'email': {'required': False},
                    'groups': {'required': False},
                    'user_permissions': {'required': False},
                    'password': {'required': False, 'write_only': True},
                }
class CollectionSummarySerializer(serializers.ModelSerializer):
    """
    Summary serializer for the Collection model, excluding related CollectionItem objects.
    This serializer is used for a lightweight representation of collections without item details.
    
    Meta:
        model: The model being serialized (Collection).
        fields: Specifies the fields to include in the serialization, excluding the items field.
    """
    class Meta:
        model = Collection
        fields = ['id', 'name', 'school', 'grade']
class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Organization model.
    """
    collection = CollectionSummarySerializer(many=True, read_only=True, source='organizations')
    class Meta:
        model = Organization
        fields = '__all__'
        extra_kwargs = {
            'password': {'required': False, 'write_only': True},
        }

# class DepartmentSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the Department model.
#     """
#     class Meta:
#         model = Department
#         fields = '__all__'

class AdminSerializer(serializers.ModelSerializer):
    """
    Serializer for the Admin model.
    """
    class Meta:
        model = Admin
        fields = '__all__'
        extra_kwargs = {
            'password': {'required': False, 'write_only': True},
        }
class IndividualSummarySerializer(serializers.ModelSerializer):
    """
    Summary serializer for the Individual model.
    Provides only key fields for a brief overview.
    """
    class Meta:
        model = Individual
        fields = ['id', 'username', 'email', 'date_of_birth']


class OrganizationSummarySerializer(serializers.ModelSerializer):
    """
    Summary serializer for the Organization model.
    Provides only key fields for a brief overview.
    """
    collection = CollectionSummarySerializer(many=True, read_only=True, source='organizations')
    class Meta:
        model = Organization
        fields = ['id', 'username', 'email', 'organization_name', 'location', 'verified','level','curriculum','collection','address','image','status']

class AdminSummarySerializer(serializers.ModelSerializer):
    """
    Summary serializer for the Admin model.
    Provides only key fields for a brief overview.
    """
    class Meta:
        model = Admin
        fields = ['id', 'username', 'email', 'admin_code']