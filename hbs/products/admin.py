from django.contrib import admin
from .models import Item, Collection, CollectionItem

class CollectionItemInline(admin.TabularInline):
    """
    Inline admin interface for CollectionItem objects.
    Allows editing of CollectionItem objects directly in the Collection admin interface.
    """
    model = CollectionItem
    extra = 1  # Number of empty forms to display in the inline formset
    min_num = 1  # Minimum number of collection items required
    autocomplete_fields = ['item']  # Autocomplete field to select the item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """
    Admin view for managing Item objects in the Django admin interface.
    
    list_display: Specifies the fields to display in the admin list view.
    search_fields: Fields to search through in the admin search bar.
    list_filter: Fields to filter by in the admin sidebar.
    """
    list_display = (
        'name', 'sku', 'price', 'category', 'visibility', 'stock_availability', 'subject', 'publisher', 'grade'
    )
    search_fields = ('name', 'sku', 'subject', 'category', 'publisher', 'grade')
    list_filter = ('visibility', 'stock_availability', 'category', 'subject', 'publisher', 'grade')
    ordering = ('name',)  # Default ordering by name


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """
    Admin view for managing Collection objects in the Django admin interface.
    
    list_display: Specifies the fields to display in the admin list view.
    search_fields: Fields to search through in the admin search bar.
    list_filter: Fields to filter by in the admin sidebar.
    """
    list_display = ('name', 'school', 'grade')
    search_fields = ('name', 'school__organization_name', 'grade')
    list_filter = ('school', 'grade')
    inlines = [CollectionItemInline]  # Add the inline to the Collection admin
    ordering = ('name',)


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    """
    Admin view for managing CollectionItem objects in the Django admin interface.
    
    list_display: Specifies the fields to display in the admin list view.
    search_fields: Fields to search through in the admin search bar.
    list_filter: Fields to filter by in the admin sidebar.
    """
    list_display = ('collection', 'item', 'quantity', 'substitutable')
    search_fields = ('collection__name', 'item__name')
    list_filter = ('collection', 'item', 'substitutable')

