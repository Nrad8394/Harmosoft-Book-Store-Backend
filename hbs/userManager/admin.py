from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Individual, Organization, Admin
from allauth.account.models import EmailAddress

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff', 'is_superuser', 'is_admin')
    list_filter = ('user_type', 'is_active', 'is_staff', 'is_superuser', 'is_admin')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'image', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_admin', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

class IndividualAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_of_birth')
    search_fields = ('username', 'email', 'first_name', 'last_name')

class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'organization_name', 'contact_number', 'address', 'verified')
    search_fields = ('username', 'email', 'organization_name', 'contact_number')

# class DepartmentAdmin(admin.ModelAdmin):
#     list_display = ('username', 'email', 'department_name', 'organization', 'verified')
#     search_fields = ('username', 'email', 'department_name', 'organization__organization_name')

class AdminAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'admin_code')
    search_fields = ('username', 'email', 'admin_code')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Individual, IndividualAdmin)
admin.site.register(Organization, OrganizationAdmin)
# admin.site.register(Department, DepartmentAdmin)
admin.site.register(Admin, AdminAdmin)
