from django.utils import timezone
from django.db.models import Sum
from farm.models import Category, Product, Cart, Equipment, EquipmentCategory


def common_variables(request):
    
    categories = Category.objects.all()
    products = Product.objects.all()

    current_user_total_quantity = Cart.objects.filter(
        customer=request.user).aggregate(
            total_quantity=Sum("quantity"))["total_quantity"]

    equipment_categories = EquipmentCategory.objects.all()
    equipments = Equipment.objects.filter(is_available=True)

    return {
            "categories": categories,
            "products": products,
            "current_user_total_quantity": current_user_total_quantity,
            "equipment_categories": equipment_categories,
            "equipments": equipments,
            }
