from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import HotelUser, HotelVendor, Hotel, Amenity, HotelImages, HotelManager

# Customize HotelUser admin
@admin.register(HotelUser)
class HotelUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_verified', 'is_active')
    list_filter = ('is_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

    # Add custom fields to the user form
    fieldsets = UserAdmin.fieldsets + (
        ('Hotel Customer Info', {
            'fields': ('profile_picture', 'phone_number', 'email_token', 'otp', 'is_verified')
        }),
    )


# Customize HotelVendor admin
@admin.register(HotelVendor)
class HotelVendorAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'business_name', 'phone_number', 'is_verified', 'is_active')
    list_filter = ('is_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'business_name', 'phone_number')

    # Add custom fields to the user form
    fieldsets = UserAdmin.fieldsets + (
        ('Vendor Business Info', {
            'fields': ('business_name', 'profile_picture', 'phone_number', 'email_token', 'otp', 'is_verified')
        }),
    )


# Hotel admin with correct field names
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('hotel_name', 'hotel_owner', 'hotel_price', 'hotel_offer_price', 'is_active')
    list_filter = ('is_active', 'hotel_price', 'hotel_owner')
    search_fields = ('hotel_name', 'hotel_description', 'hotel_location', 'hotel_owner__business_name')
    prepopulated_fields = {'hotel_slug': ('hotel_name',)}
    filter_horizontal = ('amenities',)  # Makes amenities selection easier

    fieldsets = (
        ('Basic Information', {
            'fields': ('hotel_name', 'hotel_slug', 'hotel_description', 'hotel_owner')
        }),
        ('Pricing', {
            'fields': ('hotel_price', 'hotel_offer_price')
        }),
        ('Location & Amenities', {
            'fields': ('hotel_location', 'amenities')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


# Amenity admin with correct field names
@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)
    list_per_page = 20


# HotelImages admin
@admin.register(HotelImages)
class HotelImageAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'image')
    list_filter = ('hotel',)
    search_fields = ('hotel__hotel_name',)
    readonly_fields = ['uploaded_at']




# HotelManager admin
@admin.register(HotelManager)
class HotelManagerAdmin(admin.ModelAdmin):
    list_display = ('manager_name', 'hotel', 'manager_contact')
    list_filter = ('hotel',)
    search_fields = ('manager_name', 'manager_contact', 'hotel__hotel_name')


# Customize admin site headers
admin.site.site_header = "Hotel Management System"
admin.site.site_title = "Hotel Admin"
admin.site.index_title = "Welcome to Hotel Management System"
