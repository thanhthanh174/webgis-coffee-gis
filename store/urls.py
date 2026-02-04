from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("cafes/", views.cafe_list, name="cafe_list"),
    path("book/<int:id>/", views.book, name="book"),
    path("submit-booking/", views.submit_booking, name="submit_booking"),
]
