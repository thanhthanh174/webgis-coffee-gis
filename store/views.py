from django.shortcuts import render, redirect, get_object_or_404
from maps.models import Cafe, Booking
import json
from django.shortcuts import render

def map_view(request):
    return render(request, 'maps/map.html')

def dashboard(request):
    cafes = Cafe.objects.all()
    data = [
        {
            "id": c.id,
            "name": c.name,
            "lat": c.lat,
            "lng": c.lng,
            "address": c.address,
            "opening_hours": c.opening_hours,
            "image": c.image.url if c.image else ""
        }
        for c in cafes
    ]

    return render(request, "store/dashboard.html", {
        "cafes": json.dumps(data)
    })

def cafe_list(request):
    cafes = Cafe.objects.all()
    return render(request, "store/cafe_list.html", {"cafes": cafes})


def book_form(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)
    return render(request, "store/cafe_form.html", {"cafe": cafe})


def submit_booking(request):
    if request.method == "POST":
        Booking.objects.create(
            cafe_id_id=request.POST["cafe_id"],  
            name=request.POST["name"],
            phone=request.POST["phone"],
            guests = request.POST['guests'],
            date=request.POST["date"],
            time=request.POST["time"],
        )
        return redirect("store:dashboard")
