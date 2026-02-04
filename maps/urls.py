from django.urls import path
from . import views

urlpatterns = [
    path('', views.simplemap, name="map"),
    path("api/cafes/", views.get_cafes, name="get_cafes"),
    path("api/book/", views.book, name="book"),

]
