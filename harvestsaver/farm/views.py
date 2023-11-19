from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Q, Sum
from django.db import IntegrityError

from .models import Category, Product, Cart


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
    return render(request, "farm/product_detail.html", context)

def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    quantity = request.POST.get("quantity")
    
    try:
        cart_product = Cart.objects.get(product=product, customer=request.user)
        cart_product.quantity = F("quantity") + quantity
        cart_product.save()
        cart_product.refresh_from_db()
    except Cart.DoesNotExist:
        Cart.objects.create(product=product,
                            customer=request.user,
                            quantity=quantity
                            )
    except IntegrityError as e:
        print("Error while adding to cart", e)

    current_user_total_quantity = Cart.objects.filter(
        customer=request.user).aggregate(
            total_quantity=Sum("quantity"))["total_quantity"]
     
    return redirect("farm:product_details", product.slug, product.pk)


def remove_from_cart(request, pk):
    
    product = get_object_or_404(Product, pk=pk)

    quantity = int(request.POST.get("quantity"))

    try:
        cart_product = Cart.objects.get(product=product)

        if cart_product.quantity > quantity:
            cart_product.quantity = F("quantity") - quantity
            cart_product.save()
            cart_product.refresh_from_db()
        elif cart_product.quantity <= quantity:
            cart_product.delete()
    except Cart.DoesNotExist as c:
        print("Could not remove from cart, no such product", c)
    except IntegrityError as e:
        print(e)

    return redirect("farm:product_details", product.slug, product.pk)

def delete_from_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    item = Cart.objects.get(product=product)

    item.delete()

    return redirect("farm:cart_items")


def cart_items(request):
    
    items = Cart.objects.filter(customer=request.user)
    
    total = 0
    for item in items:
        subtotal = item.calculate_total_cost
        total += subtotal

    context = {
        "items": items,
        "total": total,
        "number_of_items": items.count(),
    }
    return render(request, "farm/cart_items.html", context)






















