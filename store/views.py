from itertools import product
import profile

from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.views import LoginView
from maps.models import CafeImage, Product, Cafe, Booking, Review, ProductImage, UserProfile, BrandStory
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
import json
from django.db.models import Sum
import random
import string
from django.http import JsonResponse
import pandas as pd
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import update_session_auth_hash

from maps.models import Event, EventImage
from .forms import EventForm
from django.utils.timezone import now

# ================= USER AUTHENTICATION =================
def register(request):
    if request.method == "POST":
        username, email, p1, p2 = request.POST["username"], request.POST["email"], request.POST["password1"], request.POST["password2"]
        if p1 != p2: return render(request, "store/register.html", {"error": "Mật khẩu không khớp!"})
        if User.objects.filter(username=username).exists(): return render(request, "store/register.html", {"error": "Username đã tồn tại!"})
        User.objects.create_user(username=username, email=email, password=p1)
        return redirect("store:login")
    return render(request, "store/register.html")

class CustomLoginView(LoginView):
    template_name = 'store/login.html'

    def get_success_url(self):
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )

        if profile.must_change_password:
            return '/store/change-password/'

        if self.request.user.is_staff:
            return '/store/admin/'

        return '/store/'

@login_required
def change_password(request):
    error = None

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        if not user.check_password(old_password):
            error = "Mật khẩu hiện tại không đúng"

        elif new_password != confirm_password:
            error = "Mật khẩu mới không khớp"

        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return redirect('store:login') 

    return render(request, "store/change_password.html", {"error": error})

def custom_login_redirect(request):
    if request.user.is_staff: return redirect('store:admin_dashboard')
    return redirect('store:dashboard')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)

            new_password = ''.join(random.choices(
                string.ascii_letters + string.digits, k=8
            ))

            user.set_password(new_password)
            user.save()

            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.must_change_password = True
            profile.save()

            send_mail(
                subject="Reset mật khẩu Katinat",
                message=f"""
Chào {user.username},

Mật khẩu mới của bạn là: {new_password}

Vui lòng đăng nhập và đổi lại mật khẩu.
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "✅ Đã gửi mật khẩu mới về email!")
            return redirect("store:login")

        except User.DoesNotExist:
            messages.error(request, "❌ Email không tồn tại!")

    return render(request, "store/forgot_password.html")

# ================= USER DASHBOARD & LISTS =================
def dashboard(request):
    cafes = Cafe.objects.all()
    error_cafe = request.GET.get("error_cafe") 
    
    story = BrandStory.objects.filter(id=2).first() 

    data = [{
        "id": c.id, "name": c.name, "lat": c.lat, "lng": c.lng,
        "address": c.address, "opening_hours": c.opening_hours,
        "image": c.image.url if c.image else ""
    } for c in cafes]
    events = Event.objects.filter(is_active=True).order_by('-date')[:6]

    return render(request, "store/dashboard.html", {
        "cafes": json.dumps(data), 
        "error_cafe": error_cafe, 
        "events": events,
        "story": story  
    })

def cafe_list(request):
    cafes = Cafe.objects.all()
    paginator = Paginator(cafes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "store/cafe_list.html", {"page_obj": page_obj})

def cafe_detail(request, id):
    cafe = get_object_or_404(Cafe, id=id)
    return render(request, "store/cafe_detail.html", {
        "cafe": cafe, "products": cafe.products.all(), "gallery": cafe.images.all()
    })

# ================= BOOKING SYSTEM =================
def book_form(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)

    total = Booking.objects.filter(cafe_id=cafe).aggregate(
        total=Sum('guests')
    )['total'] or 0

    remaining = cafe.capacity - total

    return render(request, "store/cafe_form.html", {
        "cafe": cafe,
        "remaining": remaining,
        "capacity": cafe.capacity
    })

from django.db import transaction

def submit_booking(request):
    if request.method != "POST":
        return redirect("store:cafe_list")

    try:
        cafe_id = request.POST.get("cafe_id")
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        guests = request.POST.get("guests")
        date = request.POST.get("date")
        time = request.POST.get("time")
        email = request.POST.get("email")

        if not cafe_id or not name or not guests or not date or not time:
            messages.error(request, "❌ Thiếu dữ liệu!")
            return redirect("store:cafe_list")

        cafe = Cafe.objects.get(id=cafe_id)

        try:
            guests = int(guests)
            if guests <= 0:
                raise ValueError
        except:
            messages.error(request, "❌ Số người không hợp lệ!")
            return redirect("store:cafe_list")

        with transaction.atomic():

            total_guests = Booking.objects.select_for_update().filter(
                cafe_id=cafe,
                date=date,
                time=time
            ).aggregate(total=Sum('guests'))['total'] or 0

            available = cafe.capacity - total_guests

            if guests > available:
                messages.error(
                request,
                f"❌ Chi nhánh {cafe.name} chỉ còn {available} chỗ!"
            )
                return redirect(f"/store/list/?error_cafe={cafe_id}")

            booking = Booking.objects.create(
                cafe_id=cafe,
                name=name,
                phone=phone,
                guests=guests,
                date=date,
                time=time,
            )

        if email:
            send_mail(
                subject="Xác nhận đặt chỗ Katinat",
                message=f"""
Chào {name},

Bạn đã đặt chỗ thành công tại {cafe.name} 🎉

👥 Số người: {guests}
📅 Ngày: {date}
⏰ Thời gian: {time}

Cảm ơn bạn!
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=True,
            )

        messages.success(request, "🎉 Đặt chỗ thành công!")
        return redirect("store:cafe_list")

    except Exception as e:
        return HttpResponse(f"Lỗi: {e}")

# ================= CAFE MANAGEMENT (ADMIN) =================
class CafeForm(forms.ModelForm):
    class Meta:
        model = Cafe
        fields = ['name', 'address', 'image', 'lat', 'lng', 'opening_hours']

@login_required(login_url='store:login')
def admin_dashboard(request):
    query = request.GET.get('q')

    cafes = Cafe.objects.all()

    if query and query != "None":
        cafes = cafes.filter(name__icontains=query)

    paginator = Paginator(cafes, 5)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number) 

    return render(request, 'store/admin_dashboard.html', {
        'page_obj': page_obj,
        'q': query
    })

@login_required(login_url='store:login')
def add_cafe(request):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    if request.method == "POST":
        form = CafeForm(request.POST, request.FILES)

        if form.is_valid():
            cafe = form.save()

            images = request.FILES.getlist('more_images')

            for img in images:
                CafeImage.objects.create(cafe=cafe, image=img)

            return redirect('store:edit_cafe', cafe.id)

    else:
        form = CafeForm()

    return render(request, 'store/admin_add_cf.html', {'form': form})

@login_required(login_url='store:login')
def edit_cafe(request, id):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    cafe = get_object_or_404(Cafe, id=id)

    if request.method == "POST":
        form = CafeForm(request.POST, request.FILES, instance=cafe)

        if form.is_valid():
            cafe = form.save()

            images = request.FILES.getlist('more_images')

            for img in images:
                CafeImage.objects.create(cafe=cafe, image=img)

            return redirect('store:edit_cafe', cafe.id)

    else:
        form = CafeForm(instance=cafe)

    return render(request, 'store/admin_add_cf.html', {
        'form': form,
        'cafe': cafe
    })

@login_required(login_url='store:login')
def delete_cafe(request, id):
    if not request.user.is_staff: return redirect('store:dashboard')
    cafe = get_object_or_404(Cafe, id=id)
    if request.method == "POST":
        cafe.delete()
        return redirect('store:admin_dashboard')
    return render(request, 'store/admin_confirm_delete.html', {'cafe': cafe})
# ================= PRODUCT MANAGEMENT =================
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'cafes', 'name', 'price', 'image', 
            'short_desc', 'origin', 'brewing_method', 'anecdote', 'philosophy'
        ]
        widgets = {
            'cafes': forms.CheckboxSelectMultiple(), 
        }

def product_detail(request, id):
    # Liên kết ID cứng ở Trang chủ với Tên sản phẩm trong Database thật
    if id == 1:
        sp = Product.objects.filter(name__icontains="Olong").first()
        if sp: return render(request, "store/product_detail.html", {"product": sp})
        
    elif id == 2:
        sp = Product.objects.filter(name__icontains="Chôm").first()
        if sp: return render(request, "store/product_detail.html", {"product": sp})
        
    elif id == 3:
        sp = Product.objects.filter(name__icontains="D'ran").first()
        if sp: return render(request, "store/product_detail.html", {"product": sp})

    # Nếu không phải 3 ly trà nổi bật thì lấy theo ID bình thường
    product = get_object_or_404(Product, id=id)
    return render(request, "store/product_detail.html", {"product": product})

@login_required(login_url='store:login')
def admin_product(request):
    query = request.GET.get('q')
    products = Product.objects.all()

    if query and query != "None":
        products = products.filter(name__icontains=query)

    paginator = Paginator(products, 5)  # 5 sản phẩm / trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/admin_product.html', {
        'page_obj': page_obj,
        'q': query
    })

@login_required(login_url='store:login')
def select_cafes_for_product(request):
    cafes = Cafe.objects.all()
    return render(request, 'store/admin_select_cafes.html', {'cafes': cafes})

@login_required(login_url='store:login')
def add_product(request):
    selected_cafe_ids = request.GET.getlist('cafes')
    
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            images = request.FILES.getlist('images')
            for img in images:
                ProductImage.objects.create(product=product, image=img)
            return redirect('store:admin_product')
    else:
        form = ProductForm(initial={'cafes': selected_cafe_ids})

    selected_cafes_info = Cafe.objects.filter(id__in=selected_cafe_ids)

    return render(request, 'store/admin_add_pd.html', {
        'form': form, 
        'selected_cafes': selected_cafes_info
    })

@login_required(login_url='store:login')
def select_cafes_for_edit(request, id):
    product = get_object_or_404(Product, id=id)
    cafes = Cafe.objects.all()
    current_cafe_ids = list(product.cafes.values_list('id', flat=True))
    
    return render(request, 'store/admin_select_cafes_edit.html', {
        'cafes': cafes,
        'product': product,
        'current_cafe_ids': current_cafe_ids
    })

@login_required(login_url='store:login')
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    
    if 'cafes' in request.GET:
        selected_cafe_ids = request.GET.getlist('cafes')
    else:
        selected_cafe_ids = list(product.cafes.values_list('id', flat=True))

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            images = request.FILES.getlist('images')
            for img in images: 
                ProductImage.objects.create(product=product, image=img)
            delete_ids = request.POST.getlist('delete_images')
            ProductImage.objects.filter(id__in=delete_ids).delete()
            return redirect('store:admin_product')
    else: 
        form = ProductForm(instance=product, initial={'cafes': selected_cafe_ids})

    selected_cafes_info = Cafe.objects.filter(id__in=selected_cafe_ids)

    return render(request, 'store/admin_edit_pd.html', {
        'form': form, 
        'product': product,
        'selected_cafes': selected_cafes_info
    })

@login_required(login_url='store:login')
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        product.delete()
        return redirect('store:admin_product')
    return render(request, "store/admin_delete_pd.html", {"product": product})

# ================= BOOKING & REVIEW ADMIN =================
@login_required(login_url='store:login')
def admin_booking(request):
    selected_date = request.GET.get('date')
    bookings = Booking.objects.all().order_by('-date')

    if selected_date:
        bookings = bookings.filter(date=selected_date)

    paginator = Paginator(bookings, 7)  # 7 booking / trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/admin_booking.html', {
        'page_obj': page_obj,
        'selected_date': selected_date
    })

@login_required(login_url='store:login')
def delete_booking(request, id):
    if not request.user.is_staff: return redirect('store:dashboard')
    booking = get_object_or_404(Booking, id=id)
    if request.method == "POST": booking.delete()
    return redirect('store:admin_booking')

@login_required(login_url='store:login')
def admin_review(request):
    selected_cafe = request.GET.get('cafe')

    reviews = Review.objects.select_related('cafe').all().order_by('-id')

    if selected_cafe and selected_cafe != "None":
        reviews = reviews.filter(cafe_id=selected_cafe)

    paginator = Paginator(reviews, 7)  # 7 review / trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    cafes = Cafe.objects.all()

    return render(request, 'store/admin_review.html', {
        'page_obj': page_obj,
        'cafes': cafes,
        'selected_cafe': selected_cafe
    })

@login_required(login_url='store:login')
def delete_review(request, id):
    if not request.user.is_staff: return redirect('store:dashboard')
    review = get_object_or_404(Review, id=id)
    review.delete()
    return redirect('store:admin_review')

# ================= USER MANAGEMENT =================
@login_required(login_url='store:login')
def admin_user(request):
    query = request.GET.get('q')

    users = User.objects.all()

    if query and query != "None":
        users = users.filter(username__icontains=query)

    paginator = Paginator(users, 7)  # 7 user / trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/admin_user.html', {
        'page_obj': page_obj,
        'q': query
    })

@login_required(login_url='store:login')
def add_user(request):
    if request.method == "POST":
        username, email, password = request.POST.get("username"), request.POST.get("email"), request.POST.get("password")
        User.objects.create_user(username=username, email=email, password=password)
        return redirect('store:admin_user')
    return render(request, "store/admin_add_user.html")

@login_required(login_url='store:login')
def edit_user(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        user.username, user.email = request.POST.get("username"), request.POST.get("email")
        user.save()
        return redirect('store:admin_user')
    return render(request, "store/admin_edit_user.html", {"user_obj": user})

@login_required(login_url='store:login')
def delete_user(request, id):
    user = User.objects.get(id=id)
    if user != request.user: user.delete()
    return redirect('store:admin_user')

@login_required(login_url='store:login')
def toggle_role(request, id):
    user = User.objects.get(id=id)
    user.is_staff = not user.is_staff
    user.save()
    return redirect('store:admin_user')

# ================= ERROR HANDLERS =================
def custom_404(request, exception): return render(request, "404.html", status=404)
def custom_500(request): return render(request, '500.html', status=500)


def product_list(request):
    products = Product.objects.all()
    
    story = BrandStory.objects.filter(id=1).first()

    paginator = Paginator(products, 6)  # 6 sản phẩm/ 1 trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "store/products.html", {
        "page_obj": page_obj,
        "story": story 
    })

def home(request):
    cafes = Cafe.objects.all()
    return render(request, 'dashboard.html', {'cafes': cafes})

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

def admin_event_list(request):
    query = request.GET.get('q', '')
    if query:
        events = Event.objects.filter(title__icontains=query).order_by('-date')
    else:
        events = Event.objects.all().order_by('-date')
    
    paginator = Paginator(events, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'store/admin_event_list.html', {'page_obj': page_obj})

def admin_add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            images = request.FILES.getlist('images')
            for img in images:
                EventImage.objects.create(event=event, image=img)
            return redirect('store:admin_event_list')
    else:
        form = EventForm()
    return render(request, 'store/event_form.html', {'form': form})

def admin_edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            delete_images = request.POST.getlist('delete_images')
            if delete_images:
                EventImage.objects.filter(id__in=delete_images).delete()
            images = request.FILES.getlist('images')
            for img in images:
                EventImage.objects.create(event=event, image=img)
            return redirect('store:admin_event_list')
    else:
        form = EventForm(instance=event)
    return render(request, 'store/event_form.html', {'form': form, 'event': event})

def admin_delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('store:admin_event_list')

# ================= HÀM XUẤT EXCEL 3 BÁO CÁO =================
@login_required(login_url='store:login')
def export_excel_report(request):
    if not request.user.is_staff: 
        return redirect('store:dashboard')

    bookings = Booking.objects.select_related('cafe_id').all()

    if not bookings.exists():
        messages.error(request, "Chưa có dữ liệu đặt bàn để xuất báo cáo!")
        return redirect('store:admin_booking')

    data = []
    for b in bookings:
        data.append({
            'Chi Nhánh': b.cafe_id.name,
            'Khách Hàng': b.name,
            'Số Điện Thoại': b.phone,
            'Số Khách': b.guests,
            'Ngày': b.date.strftime('%Y-%m-%d'),
            'Giờ': b.time.strftime('%H:%M')
        })
    df = pd.DataFrame(data)

    df_branch = df.groupby('Chi Nhánh').agg(
        Số_Lượt_Đặt=('Khách Hàng', 'count'),
        Tổng_Số_Khách=('Số Khách', 'sum')
    ).reset_index().sort_values(by='Tổng_Số_Khách', ascending=False)

    df_time = df.groupby('Giờ').agg(
        Số_Lượt_Đặt=('Khách Hàng', 'count'),
        Tổng_Số_Khách=('Số Khách', 'sum')
    ).reset_index().sort_values(by='Số_Lượt_Đặt', ascending=False)

    df_vip = df.groupby(['Số Điện Thoại', 'Khách Hàng']).agg(
        Số_Lượt_Đặt=('Khách Hàng', 'count'),
        Tổng_Số_Khách=('Số Khách', 'sum')
    ).reset_index().sort_values(by='Số_Lượt_Đặt', ascending=False).head(10)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f"Bao_Cao_Katinat_{now().strftime('%Y%m%d')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df_branch.to_excel(writer, sheet_name='1. Độ Hot Chi Nhánh', index=False)
        df_time.to_excel(writer, sheet_name='2. Giờ Vàng', index=False)
        df_vip.to_excel(writer, sheet_name='3. Top Khách VIP', index=False)
        df.to_excel(writer, sheet_name='4. Dữ Liệu Gốc', index=False)

    return response

# ================= TÁCH 2 HÀM TUYÊN NGÔN / TÂM THƯ =================
class BrandStoryForm(forms.ModelForm):
    class Meta:
        model = BrandStory
        fields = '__all__'

@login_required(login_url='store:login')
def admin_edit_story(request):
    story, created = BrandStory.objects.get_or_create(id=1) 
    if request.method == "POST":
        form = BrandStoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            form.save()
            return redirect('store:admin_edit_story')
    else: form = BrandStoryForm(instance=story)
    return render(request, 'store/admin_edit_story.html', {'form': form, 'title': 'Tuyên Ngôn (Trang Sản Phẩm)'})

@login_required(login_url='store:login')
def admin_edit_home_story(request):
    story, created = BrandStory.objects.get_or_create(id=2) 
    if request.method == "POST":
        form = BrandStoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            form.save()
            return redirect('store:admin_edit_home_story')
    else: form = BrandStoryForm(instance=story)
    return render(request, 'store/admin_edit_story.html', {'form': form, 'title': 'Tâm Thư (Trang Chủ)'})