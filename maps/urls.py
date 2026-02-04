from django.urls import path
from . import views

urlpatterns = [
    path("", views.simplemap, name="map"),
    path("api/book/", views.book_cafe, name="book"),
    path("api/menu/<int:cafe_id>/", views.get_menu, name="menu"),
]

