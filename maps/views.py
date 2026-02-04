from django.shortcuts import render
from django.http import JsonResponse
from .models import Cafe, Product, Booking
from .models import Cafe
from django.shortcuts import render
import json

def simplemap(request):
    cafes = Cafe.objects.all()
    data=[]
    for c in cafes:
        data.append({
            "id": c.id,
            "name": c.name,
            "lat": c.lat,
            "lng": c.lng,
            "address": c.address
        })
    return render(request,"maps/map.html",{
        "cafes_json": json.dumps(data)
    })


def get_menu(request, cafe_id):
    products = Product.objects.filter(cafe_id=cafe_id)
    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "description": p.description,
            "image": p.image.url if p.image else ""
        })
    return JsonResponse(data, safe=False)


def book_cafe(request):
    if request.method == "POST":
        Booking.objects.create(
            cafe_id=request.POST["cafe_id"],
            name=request.POST["name"],
            phone=request.POST["phone"],
            date=request.POST["date"],
            time=request.POST["time"]
        )
        return JsonResponse({"status": "ok"})
