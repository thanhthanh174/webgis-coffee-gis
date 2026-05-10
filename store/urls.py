from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "store"

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
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('change-password/', views.change_password, name='change_password'),
    path('after-login/', views.custom_login_redirect, name='after_login'),
    
    # === ĐÃ SỬA TÊN LẠI CHO KHỚP VỚI HTML ===
    path('admin/booking/', views.admin_booking, name='admin_booking'),
    path('admin/booking/delete/<int:id>/', views.delete_booking, name='delete_booking'), 
    path('admin/booking/export/', views.export_excel_report, name='export_excel_report'),
    path('admin/reviews/', views.admin_review, name='admin_review'),
    path('admin/reviews/delete/<int:id>/', views.delete_review, name='delete_review'), 
    # ========================================
    
    path('admin/product/delete/<int:id>/', views.delete_product, name='admin_delete_pd'),
    path('admin/product/add/', views.add_product, name='add_product'),
    
    # MẤY CÁI QUAN TRỌNG VỀ CHỌN QUÁN 2 BƯỚC CỦA MÀY
    path('admin/product/select-cafes/', views.select_cafes_for_product, name='select_cafes_for_product'),
    path('admin/product/edit-select-cafes/<int:id>/', views.select_cafes_for_edit, name='select_cafes_for_edit'),
    
    # USER & ADMIN PRODUCT
    path('product_list/', views.product_list, name='product_list'),
    path('admin/products/', views.admin_product, name='admin_product'),
    path('edit-product/<int:id>/', views.edit_product, name='admin_edit_pd'),
    path('admin/users/', views.admin_user, name='admin_user'),
    path('admin/users/toggle/<int:id>/', views.toggle_role, name='toggle_role'),
    path('admin/users/edit/<int:id>/', views.edit_user, name='admin_edit_user'),
    path('admin/users/delete/<int:id>/', views.delete_user, name='admin_delete_user'),
    path('admin/users/add/', views.add_user, name='admin_add_user'),
    
    # SỰ KIỆN
    path('admin/events/', views.admin_event_list, name='admin_event_list'),
    path('admin/events/add/', views.admin_add_event, name='admin_add_event'),
    path('admin/events/edit/<int:event_id>/', views.admin_edit_event, name='admin_edit_event'),
    path('admin/events/delete/<int:event_id>/', views.admin_delete_event, name='admin_delete_event'),
    
    # TÁCH RIÊNG 2 LINK SỬA DI SẢN VÀ TÂM THƯ
    path('admin/story/', views.admin_edit_story, name='admin_edit_story'),  # Sửa Tuyên ngôn (Sản phẩm)
    path('admin/home-story/', views.admin_edit_home_story, name='admin_edit_home_story'), # Sửa Tâm thư (Trang chủ)
]