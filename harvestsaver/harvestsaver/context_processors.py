from django.utils import timezone
from django.db.models import Sum
from farm.models import Category, Product, Cart, Equipment, EquipmentCategory
from farm.models import Review, FrequentQuestion


def common_variables(request):
    
    categories = Category.objects.all()[:5]
    products = Product.objects.all()

    reviews = Review.objects.all()[:5]
    questions = FrequentQuestion.objects.all()[:5]

    if request.user.is_authenticated:
        current_user_total_quantity = Cart.objects.filter(
            customer=request.user).aggregate(
                total_quantity=Sum("quantity"))["total_quantity"]
    else:
        current_user_total_quantity = 0

    equipment_categories = EquipmentCategory.objects.all()[:5]
    equipments = Equipment.objects.filter(is_available=True)

    return {
            "categories": categories,
            "products": products,
            "current_user_total_quantity": current_user_total_quantity,
            "equipment_categories": equipment_categories,
            "equipments": equipments,
            "reviews": reviews,
            "questions": questions,
            }
