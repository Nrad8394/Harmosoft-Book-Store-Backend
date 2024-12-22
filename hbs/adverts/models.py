from django.db import models
from uuid import uuid4
from userManager.models import Organization  # Import Organization model for the foreign key relationship
from PIL import Image
import os

def advert_image_path(instance, filename):
    """
    Generate a unique file path for advert images.
    """
    ext = filename.split('.')[-1]
    filename = f"advert_{uuid4()}.{ext}"
    return os.path.join('adverts/', filename)

class Advert(models.Model):
    """
    Model representing an advert linked to an organization.
    """
    ADVERT_TYPE_CHOICES = [
        ('banner', 'Banner'),
        ('sidebar', 'Sidebar'),
        ('pop-up', 'Pop-up'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=advert_image_path, null=True, blank=True)
    advert_type = models.CharField(max_length=50, choices=ADVERT_TYPE_CHOICES, default='banner')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='adverts')

    def save(self, *args, **kwargs):
        """
        Override the save method to process images.
        """
        super().save(*args, **kwargs)
        
        if self.image:
            img = Image.open(self.image.path)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.thumbnail((500, 500))  # Resize the image
            img.save(self.image.path)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Advert"
        verbose_name_plural = "Adverts"
        ordering = ['-created_at']
