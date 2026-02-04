from django.shortcuts import render
from maps.models import Cafe

def dashboard(request):
    cafes = Cafe.objects.all()
    return render(request, "store/dashboard.html", {"cafes": cafes})
