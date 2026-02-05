from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Avg
import json
from .models import Booking, Cafe, Review

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
            # Thêm giờ mở cửa vào đây để bản đồ có thể đọc được
            "opening_hours": c.opening_hours,
            "image": c.image.url if c.image else ""
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
            "address": c.address,
            "lat": c.lat,
            "lng": c.lng,
            "opening_hours": c.opening_hours, # Cập nhật cho cả API
            "image": c.image.url if c.image else ""
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

# ================= THÊM REVIEW =================
@csrf_exempt
def add_review(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            cafe_id = data.get("cafe_id") 
            rating = data.get("rating")
            comment = data.get("comment", "")
            name = data.get("name", "Khách ẩn danh")

            if not cafe_id or rating is None:
                return JsonResponse({"error": "Thiếu mã quán hoặc điểm đánh giá"}, status=400)

            cafe_obj = Cafe.objects.get(id=cafe_id)

            Review.objects.create(
                cafe=cafe_obj,
                name=name,
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
        {"name": "Trà Oolong", "price": 35000},
        {"name": "Trà sữa chôm chôm", "price": 39000},
        {"name": "Cà phê sữa", "price": 29000},
    ]
    return JsonResponse(data, safe=False)


def map_view(request):
    return render(request, "maps/map.html")

