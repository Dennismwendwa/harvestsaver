from datetime import datetime
from decimal import Decimal
import requests
import json
from geopy.geocoders import Nominatim
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone

from payment.models import order_payment
from ..models import Category, Product, Cart
from ..models import EquipmentCategory, Equipment, EquipmentInquiry, EquipmentRental
from ..forms import ProductForm, EquipmentForm, EquipmentInquiryForm
from transit.services import cart_deliery_type



def succes_page(request):
    """This is success page after successfull payment"""
    return render(request, "farm/farm/success_page.html")


def home(request):
    """
    This is the home page view
    data is passed through context processor
    """

    context = {}
    return render(request, "farm/farm/index.html", context)



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
    return render(request, "farm/farm/all_products.html", context)

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
    return render(request, "farm/farm/all_equipments.html", context)


def prodcuts_category(request, slug):
    """This view filters all products of the given category"""
    category = Category.objects.get(slug=slug)
    cat_products = Product.objects.filter(category=category).all()
    
    context = {
        "category": category,
        "cat_products": cat_products,
    }
    
    return render(request, "farm/farm/category.html", context)


#@login_required
def product_details(request, slug, pk):
    """Show the deatils of one product at a time"""
    
    product = Product.objects.get(pk=pk)
    cart_item = None
    total_price = 0

    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(
            customer=request.user,
            product=product
        ).first()

    if cart_item:
        total_price = product.price * cart_item.quantity

    # to add recommentations here

    context = {
        "product": product,
        "cart_item": cart_item,
        "total_price": total_price,
    }
    return render(request, "farm/farm/product_detail.html", context)

#@login_required
def add_to_cart(request, pk):
    """Add the product to the cart"""

    product = get_object_or_404(Product, pk=pk)
    
    try:
        cart_product = Cart.objects.get(product=product, customer=request.user)
        cart_product.quantity = F("quantity") + 1
        cart_product.save()
        cart_product.refresh_from_db()

    except Cart.DoesNotExist:
        cart_product = Cart.objects.create(product=product,
                            customer=request.user,
                            quantity=1
                            )

    except Cart.IntegrityError as e:
        return JsonResponse({"success": False})
    
    current_user_total_quantity = Cart.objects.filter(
            customer=request.user).aggregate(
                total_quantity=Sum("quantity"))["total_quantity"]


    return JsonResponse({
        "quantity": cart_product.quantity,
        "total_cart_quantity": current_user_total_quantity if current_user_total_quantity else 0,
    })

@login_required
def remove_from_cart(request, pk):
    """
    Removes product from the cart
    When its the only product in the cart it delates the whole cart
    """
    product = get_object_or_404(Product, pk=pk)
    
    try:
        cart_product = Cart.objects.get(product=product, customer=request.user)
        cart_product.quantity = F("quantity") - 1
        cart_product.save()
        cart_product.refresh_from_db()

        if cart_product.quantity <= 0:
            cart_product.delete()
            return JsonResponse({"quantity": 0})
        
        current_user_total_quantity = Cart.objects.filter(
            customer=request.user).aggregate(
                total_quantity=Sum("quantity"))["total_quantity"]
        return JsonResponse({
            "quantity": cart_product.quantity,
            "total_cart_quantity": current_user_total_quantity,
            })
    except Cart.DoesNotExist:
        return JsonResponse({"quantity": 0})

@login_required
def delete_from_cart(request, pk):
    """Delete the product from the cart"""
    product = get_object_or_404(Product, pk=pk)

    Cart.objects.filter(
        customer=request.user,
        product=product
    ).delete()

    return redirect("farm:cart_items")


@login_required
def cart_items(request):
    """List all items in the cart"""
    user = request.user
    items = Cart.objects.filter(customer=user)
    
    total_price = Cart.total_cart_price(user)

    total_quantity = items.aggregate(total=Coalesce(Sum("quantity"), 0))["total"]

    context = {
        "items": items,
        "total": total_price,
        "number_of_items": total_quantity,
    }
    return render(request, "farm/farm/cart_items.html", context)


@login_required
def checkout(request):
    """
    Collects details about the shipping, payment type and prepair
    the items for transport upon successfull payment
    """
    user = request.user
    cart_items = Cart.objects.filter(customer=user)
    total = Cart.total_cart_price(user)
        
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
        "delivery_type": cart_deliery_type(cart_items),
    }
    return render(request, "farm/farm/chackout.html", context)


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
    return render(request, "farm/farm/category.html", context)

from ..services.inquiries import send_inquiry_email_async
def equipment_detail(request, slug):
    """This view is for equipment details inquiry"""
    user = request.user
    equipment = get_object_or_404(Equipment, slug=slug)
    
    if request.method == "POST":
        requested_start_date = request.POST.get("requested_start_date")
        requested_end_date = request.POST.get("requested_end_date")
        message = request.POST.get("message")
        
        equipment_name = equipment.name

        EquipmentInquiry.objects.create(
            equipment=equipment,
            requester=user,
            message=message,
            requested_start_date=requested_start_date,
            requested_end_date=requested_end_date,
        )

        return JsonResponse({"success": True})

    context = {
        "equipment": equipment,
    }
    return render(request, "farm/farm/equipment_detail.html", context)


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
    return render(request, "farm/farm/search.html", context)


@login_required
def farmer_dashboard(request):
    """
    This this farmers home page
    Contains activites which are only for farmers
    like uploading products
    """

    if not request.user.has_perm("farm.view_product"):
        messages.error(request, (
                                f"You do not have permission to access "
                                f"the page you requested.")
                                )

        return redirect(reverse_lazy("farm:home"))
    area_coodinates = get_lat_long("Mombasa, kenya")

    api_key ="4fa8a6b1e4dd7a76b125ed99fd728ce3"
    if area_coodinates:
        latitude = area_coodinates[0]
        longitude = area_coodinates[1]
    else:
        latitude = 51.51
        longitude = -0.13

    agro_weather_data = get_agro_weather(api_key, latitude, longitude)
    for weather_data_item in agro_weather_data:
        timestamp = weather_data_item.get('dt', 0)
        weather_data_item['dt'] = datetime.utcfromtimestamp(timestamp)


    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"The product was saved successfuly")
            return redirect("farm:farmer_dashboard")
        else:
            return render(request, "farm/farmer_dashboard.html", {"form": form})
    
    form = ProductForm(user=request.user)
    context = {
        "form": form,
        "weather_data_list": agro_weather_data,
        'agro_weather_data': agro_weather_data,
        }
    return render(request, "farm/farm/farmer_dashboard.html", context)


def get_agro_weather(api_key, latitude, longitude):
    """This function sends request to get weather data"""

    base_url = "https://api.agromonitoring.com/agro/1.0/weather/forecast"

    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": api_key,
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def get_lat_long(location_name):
    """
    This function use the city name to get its latitude
    and longitude
    """
    geolocator = Nominatim(user_agent="my_geocoder")
    location = geolocator.geocode(location_name)

    if location:
        return location.latitude, location.longitude
    else:
        return None


@login_required
def equipment_dashboard(request):
    """This is equipment onwers dash board view"""
    user = request.user
    equipments = Equipment.objects.filter(owner=user)

    inquiry = EquipmentInquiry.objects.filter((Q(status="pending")),
                                              equipment__in=equipments)

    if not request.user.has_perm("farm.view_equipment"):
        messages.error(request, (f"You do not have permission to access "
                                 f"the requested page"
                                ))
        return redirect("farm:home")
        
    if request.method == "POST":
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"Equipment saved successfully")
            return redirect("farm:equipment_dashboard")
        else:
            return render(request, "farm/equipment_dashboard.html",
                          {"form": form})
    
    form = EquipmentForm(user=request.user)

    context = {
        "equipments": equipments,
        "form": form,
        "inquiry": inquiry,
    }
    return render(request, "farm/farm/equipment_dashboard.html", context)


def equipment_inquiry_respond(request, slug, pk):
    """view to respond to equipment inquary"""
    user = request.user
    inquiry = get_object_or_404(EquipmentInquiry,
        pk=pk, equipment__owner=user,
    )

    if request.method == "POST" and inquiry.status != "pending":
        messages.warning(request, "This inquiry has already been responded to.")
        return redirect(
            "farm:equipment_inquiry",
            slug = inquiry.equipment.slug,
            pk = inquiry.pk
            )
    
    if request.method == "POST":
        response = request.POST.get("response")
        status = "responded"

        if not response:
            messages.error(request, "Response message cannot be empty.")
            return redirect(request.path)
        
        inquiry.response = response
        inquiry.status = status
        inquiry.responded_at = timezone.now()
        inquiry.save()

        """
        send_mail(
            subject=f"Response to your inquiry: {inquiry.subject}",
            message=response,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[inquiry.email],
            fail_silently=False,
        )"""
        messages.success(request, "Inquiry responded successfully.")
        return redirect("farm/farm:equipment_dashboard")
    
    context = {
        "inquiry": inquiry,
    }
    return render(request, "farm/farm/equipment_inquiry_respond.html", context)

