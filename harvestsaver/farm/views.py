from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import F, Q, Sum
from django.db import IntegrityError
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from payment.models import order_payment
from .models import Category, Product, Cart, Order, OrderItem
from .models import EquipmentCategory, Equipment
from .forms import ProductForm


def succes_page(request):
    return render(request, "farm/success_page.html")


def home(request):

    context = {}
    return render(request, "farm/index.html", context)


def all_products(request):
    """List all product with pagination of 4 per page"""
    products = Product.objects.all()

    products_per_page = 4
    page_number = request.GET.get("page")
    paginator = Paginator(products, products_per_page)

    page_object = paginator.get_page(page_number)
    
    context = {
        "page_object": page_object,
    }
    return render(request, "farm/all_products.html", context)

def all_equipments(request):
    """List all equipments with pagination of 4 per page"""
    equipments = Equipment.objects.all()
    
    equipments_per_page = 4
    page_number = request.GET.get("page")
    paginator = Paginator(equipments, equipments_per_page)

    page_object = paginator.get_page(page_number)
    
    context = {
        "page_object": page_object,
    }
    return render(request, "farm/all_equipments.html", context)


def prodcuts_category(request, slug):
    """This view filters all products of the given category"""
    category = Category.objects.get(slug=slug)
    cat_products = Product.objects.filter(category=category).all()
    
    context = {
        "category": category,
        "cat_products": cat_products,
    }
    
    return render(request, "farm/category.html", context)


@login_required
def product_details(request, slug, pk):
    """Show the deatils of one product at a time"""
    
    product = Product.objects.get(pk=pk)

    # to add recommentations here

    context = {
        "product": product,
    }
    return render(request, "farm/product_detail.html", context)


def add_to_cart(request, pk):
    """Add the product to the cart"""
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
    except Cart.IntegrityError as e:
        print("Error while adding to cart", e)
        messages.error(request, f"Adding to cart failed. Try agin")
        return redirect("farm:product_details", product.slug, product.pk)

    current_user_total_quantity = Cart.objects.filter(
        customer=request.user).aggregate(
            total_quantity=Sum("quantity"))["total_quantity"]
     
    return redirect("farm:product_details", product.slug, product.pk)


def remove_from_cart(request, pk):
    """
    Removes product from the cart
    When its the only product in the cart it delates the whole cart
    """
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
    """Delete the product from the cart"""
    product = get_object_or_404(Product, pk=pk)

    item = Cart.objects.get(product=product)

    item.delete()

    return redirect("farm:cart_items")


@login_required
def cart_items(request):
    """List all items in the cart"""
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


@login_required
def checkout(request):
    """
    Collects details about the shipping, payment type and prepair
    the items for transport upon successfull payment
    """
    cart_items = Cart.objects.filter(customer=request.user).all()
    
    if cart_items:
        total = 0
        for item in cart_items:
            subtotal = item.calculate_total_cost
            total += subtotal
        
    shipping = round((Decimal(3 / 100) * total), 2)
    total_cost = (total + shipping)

    if request.method == "POST":
        shipping_address = request.POST.get("address")
        payment_method = request.POST.get("payment_method", "card")
        transport = request.POST.get("transport_option")
        pickup_location= request.POST.get("pickup_location")

        
        payment_status, pk = order_payment(shipping_address,payment_method,
                                       transport, pickup_location,
                                       request)
        

        return redirect("payment:servicepayment", pk)

    context = {
        "total": total,
        "shipping": shipping,
        "total_cost": total_cost,
    }
    return render(request, "farm/chackout.html", context)


def equipment_category(request, slug):
    """Groups equipments in their different categories"""
    flag = "equipment"

    equip_category = get_object_or_404(EquipmentCategory, slug=slug)
    
    equipments = Equipment.objects.filter(category=equip_category,
                                          is_available=True)
    context = {
        "flag": flag,
        "category": equip_category,
        "equipments": equipments,
    }
    return render(request, "farm/category.html", context)


def equipment_detail(request, slug):
    """This view is for equipment details inquiry"""
    
    equipment = get_object_or_404(Equipment, slug=slug)
    
    if request.method == "POST":
        customer_name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        equipment_name = equipment.name

        email_message = (
                         f"Name: {customer_name}\nEmail: "
                         f"{email}\nSubject: {subject} "
                         f"\n\n{message}"
                         )

        send_mail(
            subject = f"Contacting about machine {equipment_name}",
            message = email_message,
            from_email = email,
            recipient_list = ["dennismusembi2@gmail.com",
                              "dennissoftware3@gmail.com",],
            fail_silently = False,
            )

    context = {
        "equipment": equipment,
    }
    return render(request, "farm/equipment_detail.html", context)


def search(request):
    """
    This view is for searching the database for any matching results
    fields to search:
        name field, description field, price field
    """
    
    if request.method == "POST":
        query = request.POST.get("query")
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query) |
            Q(price__icontains=query)
        )
        context = {
            "results": results,
            "query": query,
        }
        return render(request, "farm/search.html", context)

    context = {}
    return render(request, "farm/search.html", context)



# login_url=reverse_lazy("farm:home"),
@login_required
def farmer_dashboard(request):
    """
    This this farmers home page
    Contains activites which are only for farmers
    like uploading products
    """
    
    if not request.user.has_perm("farm.view_product"):
        print("home")
        messages.error(request, (
                                f"You do not have permission to access "
                                f"the page you requested.")
                                )

        return redirect(reverse_lazy("farm:home"))

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
        else:
            return render(request, "farm/farmer_dashboard.html", {"form": form})
    
    form = ProductForm()
    context = {"form": form}
    return render(request, "farm/farmer_dashboard.html", context)





























