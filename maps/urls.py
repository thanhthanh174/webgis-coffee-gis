from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    path("", views.simplemap, name="map"),
    path("api/book/", views.book_cafe, name="book"),
    path("api/menu/<int:cafe_id>/", views.get_menu, name="menu"),
    path('maps/', views.map_view, name='map'),
    path("api/review/add/", views.add_review, name="add_review"),
    path("api/review/<int:cafe_id>/", views.get_reviews, name="get_reviews"),
]