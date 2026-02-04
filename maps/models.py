from django.db import models

class Cafe(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()

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


class Booking(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
