from django.shortcuts import render, redirect
from .models import Category, Product


def home(request):
    context = {}
    return render(request, "farm/index.html", context)


def prodcuts_category(request, slug):
    """This view filters all products of the given category"""
    category = Category.objects.get(slug=slug)
    cat_products = Product.objects.filter(category=category).all()
    
    context = {
        "category": category,
        "cat_products": cat_products,
    }
    
    return render(request, "farm/category.html", context)


def product_details(request, slug, pk):
    
    product = Product.objects.get(pk=pk)

    # to add recommentations here

    context = {
        "product": product,
    }
    return render(request, "farm/product_details.html", context)
