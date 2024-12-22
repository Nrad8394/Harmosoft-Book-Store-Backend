from warnings import simplefilter
from django.db import models
import uuid
import os
from PIL import Image
import random
import string
from userManager.models import Organization
from django.core.exceptions import ValidationError
from sklearn.cluster import KMeans
import numpy as np
from decimal import Decimal, InvalidOperation

def item_image_path(instance, filename):
    """
    Generates a unique file path for item images based on the instance name and a UUID.
    
    Args:
        instance: The instance of the model calling the function.
        filename (str): The original name of the file being uploaded.

    Returns:
        str: A unique file path for the uploaded item image.
    """
    ext = filename.split('.')[-1]
    filename = f"{instance.name}_{uuid.uuid4()}.{ext}"
    return os.path.join('Shop/Items/', filename)


def generate_unique_code():
    """Generate a unique 6-character alphanumeric code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class Item(models.Model):
    """
    Represents a base model for shop items.

    Attributes:
        name (str): Name of the item.
        sku (UUID): Unique identifier for the item (SKU).
        description (str): A short description of the item.
        price (Decimal): Price of the item.
        visibility (bool): Whether the item is visible to users.
        stock_availability (bool): Availability of the item in stock.
        image (ImageField): Image representing the item.
        subject (str): Subject category for the item (default: 'N/A').
        publisher (str): Publisher of the item (default: 'N/A').
        category (str): Category of the item.
        grade (str): Grade level for the item.
        study_level (str): The study level for which the item is suitable.
        curriculum (str): The curriculum the item belongs to.
        cluster (str): The cluster the item belongs to.
        tag (str): Used to group items eg pen bycommon names.
        discount(Decimal): discount for eac item in %
    """
    CATEGORY_CHOICES = [
        ('Textbooks', 'Textbook'),
        ('Workbooks', 'Workbooks'),
        ('Exercise Books', 'Exercise Books'),
        ('Reference', 'Reference Books'),
        ('Teachers Guide', "Teacher's Guide"),
        ('Stationery', 'Stationery'),
        ('Storybooks', 'Storybook'),
        ('Electronics', 'Electronics'),
        ('Bags', 'Bags'),
    ]
    STUDY_LEVEL_CHOICES = [
        ('ALL', 'ALL'),
        ('ECDE & Pre-Primary', 'ECDE & Pre-Primary'),# playgroup pp1,pp2
        ('Primary School', 'Primary School'),# gd1,gd2,gd3,gd4
        ('Junior School', "Junior School"),# gd5,gd6,gd7,gd8
        ('Secondary School', 'Secondary School'),# gd9,gd10,gd11,gd12
        ('Higher Education', 'Higher Education'),
    ]
    CURRICULUM_CHOICES = [
        ('CBC', 'CBC'),
        ('IGCSE', "IGCSE"),
        ('ALL', 'ALL'),
    ]
    GRADE_CHOICES = [
        ('ALL', 'ALL'),
        ('Play Group', 'Play Group'),
        ('Pre-Primary 1', "Pre-primary one"),
        ('Pre-Primary 2', 'Pre-primary two'),
        ('Grade 1', 'Grade One'),
        ('Grade 2', 'Grade Two'),
        ('Grade 3', 'Grade Three'),        
        ('Grade 4', "Grade Four"),
        ('Grade 5', 'Grade Five'),
        ('Grade 6', 'Grade Six'),
        ('Grade 7', 'Grade Seven'),
        ('Grade 8', "Grade Eight"),
        ('Grade 9', 'Grade Nine'),
        ('Grade 10', 'Grade Ten'),
        ('Grade 11', 'Grade Eleven'),
        ('Grade 12', 'Grade Twelve'),
    ]
    name = models.CharField(max_length=100, blank=False, null=False)
    sku = models.CharField(max_length=6, unique=True, editable=False, blank=True,primary_key=True)
    ISBN = models.CharField(max_length=15, blank=True, null=True, unique=True)
    description = models.TextField(max_length=1500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    visibility = models.BooleanField(default=False)
    stock_availability = models.BooleanField(default=False)
    image = models.ImageField(
        null=True, blank=True, default='res/default.jpg', upload_to=item_image_path
    )
    subject = models.CharField(max_length=100, default='N/A')
    publisher = models.CharField(max_length=100, default='N/A')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Textbooks')
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default='All')
    study_level = models.CharField(max_length=20, choices=STUDY_LEVEL_CHOICES, default='All')
    curriculum = models.CharField(max_length=20, choices=CURRICULUM_CHOICES, default='All')
    cluster = models.CharField(max_length=20, default='Economy Pack')  
    tag = models.CharField(max_length=40, default='N/A')
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
    _cluster_assigned = False
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    def save(self, *args, **kwargs):
        """
        Overrides the save method to generate unique 6-character codes for both id and sku
        """
        # Generate unique SKU if not already set
        if not self.sku:
            self.sku = self.generate_unique_field('sku')
        # Call super save method to save the instance
        super(Item, self).save(*args, **kwargs)
    def reassign_clusters(self):
        """
        Reassigns the price cluster for all items in the database with the same 
        tag, category, subject, grade, and curriculum.
        """
        # Get all items that are similar based on tag, category, subject, grade, and curriculum
        all_items = Item.objects.filter(
            tag=self.tag,
            category=self.category,
            subject=self.subject,
            grade=self.grade,
            curriculum=self.curriculum
        )
        
        if all_items.count() >= 3:
            # Extract the prices for clustering
            prices = np.array([float(item.price) for item in all_items]).reshape(-1, 1)
            
            # Perform KMeans clustering
            kmeans = KMeans(n_clusters=3)
            kmeans.fit(prices)
            clusters = kmeans.predict(prices)
            
            # Sort clusters based on ascending price order
            sorted_clusters = np.argsort(kmeans.cluster_centers_.flatten())
            cluster_labels = {
                sorted_clusters[0]: 'Economy Pack',
                sorted_clusters[1]: 'Value Pack',
                sorted_clusters[2]: 'Premium Pack'
            }

            # Assign the new cluster to each item
            for item, cluster in zip(all_items, clusters):
                item.cluster = cluster_labels[cluster]
                item.save()  # Save the item with the updated cluster
                
        else:
            # If not enough items, assign default cluster
            for item in all_items:
                item.cluster = 'Economy Pack'
                item.save()

    def generate_unique_field(self, field_name):
        """Generate a unique 6-character alphanumeric code for a field."""
        code = generate_unique_code()
        while Item.objects.filter(**{field_name: code}).exists():
            code = generate_unique_code()
        return code

    def __str__(self):
        return self.name
    def get_substitute_or_suggestion(self,substitutable):
        """
        Returns a substitute item if the item is substitutable, otherwise provides recommendations.
        
        Recommendations are based on similar items with the same category, tag, or subject.
        """
        if substitutable:
            # Find substitute items in the same price cluster
            substitutes = Item.objects.filter(
                category=self.category,
                tag=self.tag,
                cluster=self.cluster  # Same price cluster
            ).exclude(id=self.sku)  # Exclude the current item
            if substitutes.exists():
                return substitutes

        # If not substitutable, suggest similar items (recommendations)
        suggestions = Item.objects.filter(
            category=self.category,
            subject=self.subject,
            grade=self.grade,
            curriculum=self.curriculum
        ).exclude(id=self.sku)[:5]  # Limit suggestions to 5 items

        return suggestions if suggestions.exists() else None
    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ['sku']

class Collection(models.Model):
    """
    Represents a collection or shopping list generated by schools.
    
    Attributes:
        id (UUID): Unique identifier for the collection.
        name (str): Name of the collection.
        school (ForeignKey): The organization (school) associated with the collection.
        grade (str): The grade level for which the collection is generated.
    """
    GRADE_CHOICES = [
        ('ALL', 'ALL'),
        ('Play Group', 'Play Group'),
        ('Pre-Primary 1', "Pre-primary one"),
        ('Pre-Primary 2', 'Pre-primary two'),
        ('Grade 1', 'Grade One'),
        ('Grade 2', 'Grade Two'),
        ('Grade 3', 'Grade Three'),        
        ('Grade 4', "Grade Four"),
        ('Grade 5', 'Grade Five'),
        ('Grade 6', 'Grade Six'),
        ('Grade 7', 'Grade Seven'),
        ('Grade 8', "Grade Eight"),
        ('Grade 9', 'Grade Nine'),
        ('Grade 10', 'Grade Ten'),
        ('Grade 11', 'Grade Eleven'),
        ('Grade 12', 'Grade Twelve'),
    ]
    id = models.CharField(max_length=6, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    school = models.ForeignKey(Organization, related_name='organizations', on_delete=models.CASCADE)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES, default='pp1')

    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "Collections"
        unique_together = ('school', 'grade')  # Enforces unique combination of school and grade

    def save(self, *args, **kwargs):
        # Ensure unique ID is generated before saving
        if not self.id:
            self.id = self.generate_unique_field('id')
        super(Collection, self).save(*args, **kwargs)
    
    def generate_unique_field(self, field_name):
        """Generate a unique 6-character alphanumeric code for a field."""
        code = generate_unique_code()
        while Collection.objects.filter(**{field_name: code}).exists():
            code = generate_unique_code()
        return code

    def clean(self):
        # Check if another collection with the same school and grade already exists
        if Collection.objects.filter(school=self.school, grade=self.grade).exclude(id=self.id).exists():
            raise ValidationError(f"A collection for {self.grade} already exists for this school.")

    def __str__(self):
        return f"{self.name} - {self.grade}"


class CollectionItem(models.Model):
    """
    Represents the relationship between an item and a collection, including quantity and substitution capabilities.
    
    Attributes:
        collection (ForeignKey): The collection to which this item belongs.
        item (ForeignKey): The item in the collection.
        quantity (int): The number of items in the collection.
        substitutable (bool): Whether the item can be substituted by other items in different price clusters.
    """
    collection = models.ForeignKey(Collection, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    substitutable = models.BooleanField(default=False)  # Field to mark if the item is substitutable

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    class Meta:
        verbose_name = "Collection Item"
        verbose_name_plural = "Collection Items"

