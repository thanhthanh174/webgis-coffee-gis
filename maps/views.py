from django.shortcuts import render
from .models import Cafe
import json
from django.http import JsonResponse
from .models import Cafe
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Booking, Cafe

def simplemap(request):
    cafes = Cafe.objects.all()
    data = [
        {"name": c.name, "lat": c.lat, "lng": c.lng, "address": c.address}
        for c in cafes
    ]
    return render(request, "maps/map.html", {
        "cafes": json.dumps(data)
    })

def get_cafes(request):
    data = list(Cafe.objects.values())
    return JsonResponse(data, safe=False)

@csrf_exempt
def book(request):
    if request.method == "POST":
        data = json.loads(request.body)

        Booking.objects.create(
            cafe_id_id=data["cafe_id"],
            name=data["name"],
            phone=data["phone"],
            people=data["people"],
            date=data["date"],
            time=data["time"],
        )

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "Invalid method"}, status=400)
