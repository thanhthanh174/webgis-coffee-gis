from django.contrib import admin
from .models import Cafe, Product, Booking, Review

admin.site.register(Booking)

@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ("name", "address")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "cafe")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "cafe", "rating", "created_at")