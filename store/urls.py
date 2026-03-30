from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = "store"
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('list/', views.cafe_list, name='cafe_list'),
    path('book/<int:cafe_id>/', views.book_form, name='book_form'),
    path('submit/', views.submit_booking, name='submit_booking'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('add/', views.add_cafe, name='add_cafe'),
    path('edit/<int:id>/', views.edit_cafe, name='edit_cafe'),
    path('delete/<int:id>/', views.delete_cafe, name='delete_cafe'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='store:login'), name='logout'),
    path('register/', views.register, name='register'),
    path('after-login/', views.custom_login_redirect, name='after_login'),
    path('admin/booking/', views.admin_booking, name='admin_booking'),
    path('admin/booking/delete/<int:id>/', views.delete_booking, name='delete_booking'),
]
