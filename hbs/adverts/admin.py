from django.contrib import admin
from .models import Advert

@admin.register(Advert)
class AdvertAdmin(admin.ModelAdmin):
    """
    Admin view for managing Adverts.
    """
    list_display = ['title', 'advert_type', 'organization', 'created_at']
    list_filter = ['advert_type', 'created_at']
    search_fields = ['title', 'organization__organization_name']
    ordering = ['-created_at']

    def get_queryset(self, request):
        """
        Customize queryset to show adverts related to the organization.
        """
        qs = super().get_queryset(request)
        if request.user.user_type == 'organization': # type: ignore
            return qs.filter(organization=request.user)
        return qs
