from django.db import models

class Cafe(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return self.name


class Booking(models.Model):
    cafe = models.ForeignKey(Cafe, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    people = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.cafe.name}"
