from django.utils import timezone
from farm.models import Category, Product

def common_variables(request):
    
    categories = Category.objects.all()
    products = Product.objects.all()

    return {
            "categories": categories,
            "products": products,
            }
