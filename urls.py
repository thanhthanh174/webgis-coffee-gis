from django.urls import include, path
from maps import views

path("store/", include("store.urls")),
path("", include("maps.urls")),
path('', views.map_view, name='home'),
