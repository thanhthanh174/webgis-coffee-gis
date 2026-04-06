from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from streamlit import form
from maps.models import Product
from maps.models import Cafe, Booking
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from maps.models import Review
from maps.models import Product

import json

# ===== REGISTER =====
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username đã tồn tại!")
            return redirect("store:register")

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Đăng ký thành công!")

        return redirect("store:login")

    return render(request, "store/register.html")


# ===== LOGIN CUSTOM =====
class CustomLoginView(LoginView):
    template_name = 'store/login.html'

    def get_success_url(self):
        if self.request.user.is_staff:
            return '/store/admin/'
        return '/store/'

def custom_login_redirect(request):
    if request.user.is_staff:
        return redirect('store:admin_dashboard')
    return redirect('store:dashboard')

# ===== ADMIN DASHBOARD =====
@login_required(login_url='store:login')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    cafes = Cafe.objects.all()
    return render(request, 'store/admin_dashboard.html', {'cafes': cafes})


# ===== DASHBOARD USER =====
def dashboard(request):
    cafes = Cafe.objects.all()

    data = [
        {
            "id": c.id,
            "name": c.name,
            "lat": c.lat,
            "lng": c.lng,
            "address": c.address,
            "opening_hours": c.opening_hours,
            "image": c.image.url if c.image else ""
        }
        for c in cafes
    ]

    return render(request, "store/dashboard.html", {
        "cafes": json.dumps(data)
    })


# ===== LIST CAFE =====
def cafe_list(request):
    cafes = Cafe.objects.all()

    paginator = Paginator(cafes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "store/cafe_list.html", {
        "page_obj": page_obj
    })


# ===== BOOKING FORM =====
def book_form(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)
    return render(request, "store/cafe_form.html", {"cafe": cafe})


# ===== SUBMIT BOOKING =====
def submit_booking(request):
    if request.method != "POST":
        return redirect("store:dashboard")

    try:
        cafe_id = request.POST.get("cafe_id")
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        guests = request.POST.get("guests")
        date = request.POST.get("date")
        time = request.POST.get("time")
        email = request.POST.get("email")

        if not cafe_id or not name or not guests:
            return HttpResponse("Thiếu dữ liệu!")

        cafe = Cafe.objects.get(id=cafe_id)

        booking = Booking.objects.create(
            cafe_id=cafe,
            name=name,
            phone=phone,
            guests=guests,
            date=date,
            time=time,
        )

        # 🔥 GỬI MAIL
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

        # 🔥 THÀNH CÔNG → VỀ DASHBOARD
        return redirect("store:dashboard")

    except Exception as e:
        # 👉 in lỗi ra để debug
        return HttpResponse(f"Lỗi: {e}")


# ===== PRODUCT DETAIL =====
def product_detail(request, id):
    products = {
        1: {
            "name": "Trà Olong Ba Lá",
            "desc": 

            "Trà Olong Ba Lá là một thức uống mang đậm phong vị trà cao cấp, kết hợp giữa sự tinh tế của trà ô long và nét thanh mát của thiên nhiên vùng cao. "
            "Lá trà được tuyển chọn kỹ lưỡng từ những đồi trà xanh mướt, nơi khí hậu mát mẻ giúp tạo nên hương vị trà đậm đà nhưng vẫn rất êm dịu.\n\n"

            "Điểm đặc biệt của thức uống nằm ở sự cân bằng giữa vị chát nhẹ ban đầu và hậu vị ngọt thanh kéo dài. "
            "Khi thưởng thức, người dùng sẽ cảm nhận được lớp hương trà sâu lắng, mang lại cảm giác thư giãn và dễ chịu.\n\n"

            "Phần kem sữa được thêm vào một cách tinh tế, giúp làm mềm vị trà và tạo nên kết cấu mượt mà. "
            "Đây là lựa chọn lý tưởng cho những ai yêu thích sự sang trọng và tinh tế trong từng ngụm trà.",

            "image": "/static/admin/images/olong-ba-la.jpg"
        },

        2: {
            "name": "Trà sữa Chôm Chôm",
            "desc":

            "Lấy cảm hứng từ trái chôm chôm nhiệt đới, thức uống này mang đến sự kết hợp độc đáo giữa vị trà sữa truyền thống và hương trái cây tươi mát. "
            "Vị ngọt dịu nhẹ hòa quyện cùng độ béo của sữa tạo nên cảm giác dễ uống và hấp dẫn.\n\n"

            "Điểm nhấn của món này là lớp topping chôm chôm giòn nhẹ, mang lại trải nghiệm thú vị khi thưởng thức. "
            "Hương vị tươi mới giúp giải nhiệt hiệu quả trong những ngày nắng nóng.\n\n"

            "Đây là lựa chọn hoàn hảo cho những ai yêu thích sự trẻ trung, mới lạ và muốn khám phá những hương vị độc đáo.",

            "image": "/static/admin/images/ts-chom-chom.jpg"
        },

        3: {
            "name": "Trà sữa Hồng D'ran",
            "desc":

            "Lấy cảm hứng từ vùng đất cao nguyên Đà Lạt, Trà sữa Hồng D'ran mang đến hương vị đậm đà và ấm áp. "
            "Sự kết hợp giữa trà đen truyền thống và sữa béo tạo nên một tổng thể hài hòa và cuốn hút.\n\n"

            "Vị trà mạnh mẽ kết hợp với độ ngọt vừa phải giúp thức uống trở nên cân bằng và dễ thưởng thức. "
            "Hương thơm nhẹ nhàng mang lại cảm giác thư giãn và dễ chịu.\n\n"

            "Đây là lựa chọn phù hợp cho những ai yêu thích phong cách cổ điển nhưng vẫn muốn trải nghiệm sự tinh tế hiện đại.",

            "image": "/static/admin/images/ts-hong-dran.jpg"
        }
    }

    product = products.get(id)

    return render(request, "store/product_detail.html", {
        "product": product
    })

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/admin_product_list.html', {
        'products': products
    })

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['cafe', 'name', 'description', 'price', 'image']

@login_required(login_url='store:login')
def add_product(request):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    form = ProductForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        return redirect('store:admin_product')

    return render(request, 'store/admin_add_pd.html', {'form': form})

# USER
def product_list(request):
    products = Product.objects.all()
    return render(request, "store/products.html", {"products": products})

@login_required(login_url='store:login')
# ADMIN
def admin_product(request):
    products = Product.objects.all()
    return render(request, "store/admin_product.html", {"products": products})

@login_required(login_url='store:login')
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()
        return redirect('store:admin_product')

    return render(request, "store/admin_delete_pd.html", {
        "product": product
    })

@login_required(login_url='store:login')
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    form = ProductForm(instance=product)

    return render(request, "store/admin_edit_pd.html", {
        "form": form,
        "product": product
    })

def cafe_detail(request, id):
    cafe = Cafe.objects.get(id=id)
    products = cafe.products.all()  # 🔥 lấy sản phẩm theo quán

    return render(request, "store/cafe_detail.html", {
        "cafe": cafe,
        "products": products
    })

# ===== FORM CAFE =====
class CafeForm(forms.ModelForm):
    class Meta:
        model = Cafe
        fields = ['name', 'address', 'image', 'lat', 'lng']


@login_required(login_url='store:login')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    cafes = Cafe.objects.all()

    # 🔥 SEARCH
    q = request.GET.get('q')
    if q:
        cafes = cafes.filter(name__icontains=q)

    return render(request, 'store/admin_dashboard.html', {
        'cafes': cafes,
        'q': q
    })

# ===== ADD CAFE =====
@login_required(login_url='store:login')
def add_cafe(request):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    form = CafeForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        return redirect('store:admin_dashboard')

    return render(request, 'store/admin_add_cf.html', {'form': form})


# ===== EDIT CAFE =====
@login_required(login_url='store:login')
def edit_cafe(request, id):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    cafe = get_object_or_404(Cafe, id=id)

    form = CafeForm(request.POST or None, request.FILES or None, instance=cafe)

    if form.is_valid():
        form.save()
        return redirect('store:admin_dashboard')

    return render(request, 'store/admin_add_cf.html', {'form': form})


# ===== DELETE CAFE =====
@login_required(login_url='store:login')
def delete_cafe(request, id):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    cafe = get_object_or_404(Cafe, id=id)

    if request.method == "POST":
        cafe.delete()
        return redirect('store:admin_dashboard')

    return render(request, 'store/admin_confirm_delete.html', {'cafe': cafe})
    


# ===== ADMIN BOOKING =====
@login_required(login_url='store:login')
def admin_booking(request):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    bookings = Booking.objects.all().order_by('-date', '-time')

    # 🔥 FILTER THEO NGÀY
    date = request.GET.get('date')
    if date:
        bookings = bookings.filter(date=date)

    return render(request, 'store/admin_booking.html', {
        'bookings': bookings,
        'selected_date': date
    })


# ===== DELETE BOOKING =====
@login_required(login_url='store:login')
def delete_booking(request, id):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    booking = get_object_or_404(Booking, id=id)

    if request.method == "POST":
        booking.delete()
        return redirect('store:admin_booking')

    return redirect('store:admin_booking')

def home(request):
    cafes = Cafe.objects.all()

    return render(request, 'dashboard.html', {
        'cafes': cafes
    })

@login_required(login_url='store:login')
def admin_review(request):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    reviews = Review.objects.select_related('cafe').all().order_by('-created_at')
    cafes = Cafe.objects.all()

    # 🔥 FILTER
    cafe_id = request.GET.get('cafe')
    if cafe_id:
        reviews = reviews.filter(cafe_id=cafe_id)

    return render(request, 'store/admin_review.html', {
        'reviews': reviews,
        'cafes': cafes,
        'selected_cafe': cafe_id
    })

@login_required(login_url='store:login')
def delete_review(request, id):
    if not request.user.is_staff:
        return redirect('store:dashboard')

    review = get_object_or_404(Review, id=id)

    review.delete()
    return redirect('store:admin_review')
