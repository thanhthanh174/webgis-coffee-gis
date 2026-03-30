from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.views import LoginView
import json
from django.shortcuts import redirect
from maps.models import Cafe, Booking


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
@login_required(login_url='store:login')
def book_form(request, cafe_id):
    cafe = get_object_or_404(Cafe, id=cafe_id)
    return render(request, "store/cafe_form.html", {"cafe": cafe})


# ===== SUBMIT BOOKING =====
def submit_booking(request):
    if request.method == "POST":
        cafe = Cafe.objects.get(id=request.POST["cafe_id"])

        Booking.objects.create(
            cafe=cafe,
            name=request.POST["name"],
            phone=request.POST["phone"],
            guests=request.POST['guests'],
            date=request.POST["date"],
            time=request.POST["time"],
        )

        return redirect("store:dashboard")


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


# ===== FORM CAFE =====
class CafeForm(forms.ModelForm):
    class Meta:
        model = Cafe
        fields = ['name', 'address', 'image', 'lat', 'lng']


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

    bookings = Booking.objects.all().order_by('-time')
    return render(request, 'store/admin_booking.html', {'bookings': bookings})


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