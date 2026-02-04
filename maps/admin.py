from django.contrib import admin
from .models import Cafe, Booking


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ("name", "address")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "cafe", "phone", "people", "date", "time")
    list_filter = ("date", "cafe")
    search_fields = ("customer_name", "phone")
