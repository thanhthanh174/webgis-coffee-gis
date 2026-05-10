from django.contrib import admin
from .models import Cafe, Product, Booking, Review, CafeImage, ProductImage

admin.site.register(Booking)
admin.site.register(CafeImage)

class CafeImageInline(admin.TabularInline):
    model = CafeImage
    extra = 10
    fields = ['image']

@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ("name", "address")
    inlines = [CafeImageInline]

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Dòng này giúp hiện bảng chọn nhiều quán nằm ngang để bạn tick ✅ cho lẹ
    filter_horizontal = ('cafes',) 
    list_display = ('name', 'price') 

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "cafe", "rating", "created_at")

