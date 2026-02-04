from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from maps.models import Cafe, Booking

def dashboard(request):
    cafes = Cafe.objects.all()
    return render(request, "store/dashboard.html", {"cafes": cafes})


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
            people=request.POST["people"],
            date=request.POST["date"],
            time=request.POST["time"],
        )
        return redirect("store:dashboard")
    
from django.shortcuts import render, get_object_or_404
from maps.models import Cafe

def book(request, id):
    cafe = get_object_or_404(Cafe, id=id)
    return render(request, "store/cafe_form.html", {"cafe": cafe})

