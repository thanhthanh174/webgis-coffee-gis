from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('list/', views.cafe_list, name='cafe_list'),
    path('book/<int:cafe_id>/', views.book_form, name='book_form'),
    path('submit/', views.submit_booking, name='submit_booking'),
    path('map/', views.map_view, name='map'),
]
