from django.urls import include, path


path("store/", include("store.urls")),
path("", include("maps.urls")),
