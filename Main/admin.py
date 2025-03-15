from django.contrib import admin
from .models import CustomUser, Category, PackageType, Package, Booking, Payment, Trainer, Product, Appointment

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')

class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer', 'price', 'bookings_count_display', 'category', 'package_type', 'duration', 'available')

    def bookings_count_display(self, obj):
        return obj.bookings_count  # Calls the property method from the model

    bookings_count_display.short_description = "Bookings Count"

# ✅ Correct way to register admin classes
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Package, PackageAdmin)  # ✅ Register Package with PackageAdmin
admin.site.register(Category)
admin.site.register(PackageType)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Trainer)
admin.site.register(Product)
admin.site.register(Appointment)
