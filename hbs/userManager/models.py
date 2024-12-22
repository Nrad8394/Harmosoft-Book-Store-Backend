from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth.hashers import make_password
import uuid
import os
from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError

def user_profile_image_path(instance, filename):
    """
    Generate a unique file path for user profile images.

    Args:
        instance (CustomUser): The instance of the user.
        filename (str): The original filename.

    Returns:
        str: A new file path for the uploaded image.
    """
    ext = filename.split('.')[-1]
    filename = f"{instance.username}_{uuid.uuid4()}.{ext}"
    return os.path.join('users/', filename)

class CustomUser(AbstractUser):
    """
    Custom user model that extends the default Django AbstractUser.
    """
    USER_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('organization', 'Organization'),
        ('admin', 'Admin'),
    )
    image = models.ImageField(null=True, blank=True, default='res/default.png', upload_to=user_profile_image_path)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, default='individual')
    groups = models.ManyToManyField(Group, related_name='customuser_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_permissions')
    is_admin = models.BooleanField(default=False)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contact_number = PhoneNumberField(blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)  # Ensure uniqueness in the database

    def save(self, *args, **kwargs):
        """
        Override save method to hash passwords and process images. 
        Manually check for email uniqueness before saving.
        """
        # Check for email uniqueness manually
        if CustomUser.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError(f"A user with email {self.email} already exists.")

        # Hash password if not hashed already
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)

        # Process image (resize if necessary)
        if self.image:
            img = Image.open(self.image.path)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.thumbnail((300, 300))
            img.save(self.image.path)

        # Call the parent save method
        super().save(*args, **kwargs)
class Individual(CustomUser):
    """
    Model for individual users.
    """
    date_of_birth = models.DateField(blank=False, null=True)

    class Meta:
        verbose_name = "Individual"
        verbose_name_plural = "Individuals"

class Organization(CustomUser):
    """
    Model for organization users.
    """
    LOCATION_CHOICES = [
        ('Nairobi', 'Nairobi Metropolitan'),
        ('Nakuru', "Nakuru one"),
        ('Mombasa', 'Mombasa'),
        ('Kisumu', 'Kisumu'),
    ]
    LEVEL_CHOICES = [
        ('All', 'ALL'),
        ('ECDE & Pre-Primary', 'ECDE & Pre-Primary'),
        ('Primary School', 'Primary School'),
        ('Junior Secondary', "Junior School"),
        ('Secondary School', 'Secondary School'),
    ]
    CIRRICULUM_CHOICES = [
        ('CBC', 'CBC'),
        ('IGCSE', "IGCSE"),
        ('ALL', 'ALL'),
    ]   
    STATUS_CHOICES = [
        ('Private', 'Private'),
        ('Public', "Public"),
    ]
    status = models.CharField(max_length=50, choices=LEVEL_CHOICES , default="Private")
    organization_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    verified = models.BooleanField(default=False)
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES , default="nairobi")
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES , default="preprimary")
    curriculum = models.CharField(max_length=50, choices=CIRRICULUM_CHOICES , default="all")
    
    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"

class Admin(CustomUser):
    """
    Model for admin users.
    """
    admin_code = models.UUIDField(default=uuid.uuid4, editable=False)
    permissions = models.ManyToManyField(Permission, related_name='admin_permissions')

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
