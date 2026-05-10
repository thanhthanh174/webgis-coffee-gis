from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Avg, Q
import pandas as pd
from django.http import HttpResponse
import json
from .models import Booking, Cafe, Review, Product 

# ================= MAP =================
def simplemap(request):
    cafes = Cafe.objects.all()
    data = [
        {
            "id": c.id,
            "name": c.name,
            "lat": c.lat,
            "lng": c.lng,
            "address": c.address,
            "opening_hours": c.opening_hours,
            "image": c.image.url if c.image else "",
            "images": [img.image.url for img in c.images.all()]
        }
        for c in cafes
    ]
    return render(request, "maps/map.html", {
        "cafes": json.dumps(data)
    })

# ================= API LẤY DANH SÁCH QUÁN =================
def get_cafes(request):
    cafes = Cafe.objects.all()
    data = [
        {
            "id": c.id,
            "name": c.name,
            "lat": c.lat,
            "lng": c.lng,
            "address": c.address,
            "opening_hours": c.opening_hours,
            "image": c.image.url if c.image else None,
            "images": [img.images.url for img in c.images.all() if img.images]
        }
        for c in cafes
    ]
    return JsonResponse(data, safe=False)

# ================= ĐẶT BÀN =================
@csrf_exempt
def book(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            Booking.objects.create(
                cafe_id=data["cafe_id"],
                name=data["name"],
                phone=data["phone"],
                people=data["people"],
                date=data["date"],
                time=data["time"],
                created_at=timezone.now()
            )
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid method"}, status=400)

# ================= THÊM REVIEW (ĐÃ CẬP NHẬT CHỐNG SPAM) =================
@csrf_exempt
def add_review(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cafe_id = data.get("cafe_id") 
            rating = data.get("rating")
            comment = data.get("comment", "")
            
            # Kiểm tra xem User đã đăng nhập chưa
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Bạn cần đăng nhập để đánh giá!"}, status=401)

            if not cafe_id or rating is None:
                return JsonResponse({"error": "Thiếu mã quán hoặc điểm đánh giá"}, status=400)

            # --- KHÚC BẢO VỆ "CỤC DÀNG" KHỎI SPAM ĐÂY ---
            # Kiểm tra trong DB xem User này đã đánh giá quán này (cafe_id) chưa
            da_danh_gia = Review.objects.filter(name=request.user.username, cafe_id=cafe_id).exists()
            
            if da_danh_gia:
                # Nếu đã tồn tại rồi thì chặn đứng lại, không cho tạo thêm
                return JsonResponse({
                    "error": "Bạn đã đánh giá chi nhánh này rồi, không được spam nha cục dàng!"
                }, status=400)
            # --------------------------------------------

            cafe_obj = Cafe.objects.get(id=cafe_id)

            # Nếu chưa đánh giá thì mới tạo mới
            Review.objects.create(
                cafe=cafe_obj,
                name=request.user.username,
                rating=int(rating),
                comment=comment
            )

            reviews = Review.objects.filter(cafe=cafe_obj)
            avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"] or 0

            return JsonResponse({
                "status": "success",
                "message": "Đã gửi đánh giá thành công!",
                "avg_rating": round(float(avg_rating), 1),
                "total_reviews": reviews.count()
            })
        except Cafe.DoesNotExist:
            return JsonResponse({"error": "Không tìm thấy quán cafe này"}, status=404)
        except Exception as e:
            print(f"LỖI TẠI SERVER: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method không hợp lệ"}, status=405)

# ================= LẤY REVIEW =================
def get_reviews(request, cafe_id):
    reviews = Review.objects.filter(cafe_id=cafe_id).order_by("-created_at")
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"] or 0
    
    review_list = [
        {
            "name": r.name,
            "rating": int(r.rating),
            "comment": r.comment,
            "created_at": r.created_at.strftime("%d/%m/%Y %H:%M") if r.created_at else ""
        }
        for r in reviews
    ]

    return JsonResponse({
        "avg_rating": round(float(avg_rating), 1),
        "reviews": review_list
    })


# ================= ĐẶT BÀN =================
def book_cafe(request):
    if request.method == "POST":
        Booking.objects.create(
            cafe_id_id=request.POST["cafe_id"],
            name=request.POST["name"],
            phone=request.POST["phone"],
            guests=request.POST["people"],  
            date=request.POST["date"],
            time=request.POST["time"],
        )
        return JsonResponse({"status": "ok"})


def get_menu(request):
    data = [
        {"name": "Trà Oolong", "price": 55000},
        {"name": "Trà sữa chôm chôm", "price": 60000},
        {"name": "Cà phê sữa", "price": 55000},
    ]
    return JsonResponse(data, safe=False)


def map_view(request):
    return render(request, "maps/map.html")

 
def export_excel(request):
    branch = request.GET.get('branch')

    queryset = Cafe.objects.all()

    if branch:
        queryset = queryset.filter(name__icontains=branch)

    data = queryset.values('name', 'address', 'lat', 'lng', 'capacity', 'opening_hours')
    df = pd.DataFrame(list(data))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="danh_sach_cafe.xlsx"'

    df.to_excel(response, index=False)
    return response

def export_booking_excel(request):
    date = request.GET.get('date')

    queryset = Booking.objects.all()

    if date:
        queryset = queryset.filter(date=date)

    data = queryset.values(
        'name',
        'phone',
        'guests',
        'date',
        'time',
        'cafe_id__name'
    )

    df = pd.DataFrame(list(data))

    df.columns = ['Tên khách', 'SĐT', 'Số người', 'Ngày', 'Giờ', 'Chi nhánh']

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="booking.xlsx"'

    df.to_excel(response, index=False)
    return response