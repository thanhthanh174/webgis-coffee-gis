from django.db import models
from django.contrib.auth.models import User

class Cafe(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()
    image = models.ImageField(upload_to="cafes/", blank=True, null=True)
    opening_hours = models.CharField(max_length=100, default="08:00 - 22:00") 
    capacity = models.IntegerField(default=35) 

    def __str__(self):
        return self.name

class CafeImage(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cafes/gallery/', blank=True, null=True)
    
    def __str__(self):
        return f"Ảnh của {self.cafe.name}"

class Product(models.Model):
    cafes = models.ManyToManyField(Cafe, related_name='products', blank=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    # 5 Ô NHẬP LIỆU RIÊNG BIỆT CHO "KHÁM PHÁ MỸ VỊ" - Thay thế description cũ
    short_desc = models.CharField(max_length=255, blank=True, null=True, verbose_name="1. Mô tả ngắn")
    origin = models.TextField(blank=True, null=True, verbose_name="2. Nguồn gốc")
    brewing_method = models.TextField(blank=True, null=True, verbose_name="3. Tâm pháp pha chế")
    anecdote = models.TextField(blank=True, null=True, verbose_name="4. Giai thoại")
    philosophy = models.TextField(blank=True, null=True, verbose_name="5. Cảm thức nhân sinh")

    def __str__(self):
        return self.name
    
# CÁI NÀY CỦA BẠN ĐỂ LƯU NHIỀU ẢNH (CAROUSEL) - GIỮ NGUYÊN 100%
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')

    def __str__(self):
        return f"Ảnh của {self.product.name}"

class Review(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name="reviews")
    name = models.CharField(max_length=100)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating}⭐"

class Booking(models.Model):
    cafe_id = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    guests = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()

class Branch(models.Model):
    name = models.CharField(max_length=100)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    must_change_password = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    
class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Tên sự kiện")
    short_description = models.CharField(max_length=255, verbose_name="Mô tả ngắn", null=True, blank=True)
    content = models.TextField(verbose_name="Nội dung chi tiết")
    date = models.DateField(verbose_name="Ngày diễn ra")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị trên trang chủ")
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='events/main/', blank=True, null=True, verbose_name="Ảnh chính")
    def __str__(self):
        return self.title

class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='events/', verbose_name="Ảnh sự kiện")
    def __str__(self):
        return f"Ảnh của {self.event.title}"


# ==========================================
# BẢNG MỚI: DÀNH CHO KATINAT DI SẢN (Nằm riêng biệt, độc lập)
# ==========================================
class BrandStory(models.Model):
    main_title = models.CharField(max_length=255, default="KATINAT - BẢN TUYÊN NGÔN DI SẢN VÀ NGHỆ THUẬT GIAO THOA ĐA TẦNG", verbose_name="Tiêu đề chính")
    
    # Đoạn 1
    image_1 = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name="Ảnh 1 (Quán Katinat)")
    text_1 = models.TextField(blank=True, null=True, verbose_name="Đoạn văn 1")
    
    # Đoạn 2
    image_2 = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name="Ảnh 2 (Pha trà)")
    title_2 = models.CharField(max_length=255, default="🍃 Tinh Tuyển Từ Nguồn Gốc - Lời hồi đáp từ đất mẹ linh thiêng", verbose_name="Tiêu đề đoạn 2")
    text_2 = models.TextField(blank=True, null=True, verbose_name="Đoạn văn 2")
    
    # Đoạn 3
    image_3 = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name="Ảnh 3 (Ly cờ đỏ)")
    title_3 = models.CharField(max_length=255, default="🥛 Nghệ Thuật Phối Trộn Đa Tầng - Bản giao hưởng của những giác quan đương đại", verbose_name="Tiêu đề đoạn 3")
    text_3 = models.TextField(blank=True, null=True, verbose_name="Đoạn văn 3")
    
    # Đoạn 4
    image_4 = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name="Ảnh 4 (Đồng hồ/Không gian)")
    title_4 = models.CharField(max_length=255, default="✨ Hơn Cả Một Vị Giác - Điểm chạm của cảm xúc và phong cách sống", verbose_name="Tiêu đề đoạn 4")
    text_4 = models.TextField(blank=True, null=True, verbose_name="Đoạn văn 4")
    
    #đoạn 5
    title_5 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tiêu đề đoạn 5")
    image_5 = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name="Ảnh 5")
    text_5 = models.TextField(blank=True, null=True, verbose_name="Đoạn văn 5")

    title_6 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tiêu đề đoạn 6")
    image_6 = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name="Ảnh 6")
    text_6 = models.TextField(blank=True, null=True, verbose_name="Đoạn văn 6")

    title_7 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tiêu đề đoạn 7")
    image_7 = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name="Ảnh 7")
    text_7 = models.TextField(blank=True, null=True, verbose_name="Đoạn văn 7")

    title_8 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tiêu đề đoạn 8")
    image_8 = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name="Ảnh 8")
    text_8 = models.TextField(blank=True, null=True, verbose_name="Đoạn văn 8")

    title_9 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tiêu đề đoạn 9")
    image_9 = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name="Ảnh 9")
    text_9 = models.TextField(blank=True, null=True, verbose_name="Đoạn văn 9")

    title_10 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tiêu đề đoạn 10")
    image_10 = models.ImageField(upload_to='stories/', blank=True, null=True, verbose_name="Ảnh 10")
    text_10 = models.TextField(blank=True, null=True, verbose_name="Đoạn văn 10")

    def __str__(self):
        return "Bài viết Tuyên Ngôn Di Sản"