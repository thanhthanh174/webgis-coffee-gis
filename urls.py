from django.urls import include, path
from maps import views

path("store/", include("store.urls")),
path("", include("maps.urls")),
path('', views.map_view, name='home'),
handler404 = 'store.views.custom_404'
handler500 = 'store.views.custom_500'