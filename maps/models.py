from django.db import models

class Cafe(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()
    image = models.ImageField(upload_to="cafes/", blank=True, null=True)
    opening_hours = models.CharField(max_length=100, default="08:00 - 22:00") 

    def __str__(self):
        return self.name

class Product(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return self.name

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
