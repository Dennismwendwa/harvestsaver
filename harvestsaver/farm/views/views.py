from itertools import groupby
from operator import attrgetter

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.conf import settings
from django.core.cache import cache

from payment.models import Payout
from ..models import Category, Product, Cart, Farm, OrderItem, Order
from ..models import EquipmentCategory, Equipment, EquipmentInquiry
from logistics.models import Location
from ..forms import ProductForm, EquipmentForm, FarmForm
from transit.services import cart_deliery_type, process_order
from ..utils.utils import weather_data, assign_hub_to_farm, get_default_range
from farm.services.functions import reduce_stock_for_order



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

    products_per_page = 8
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
    from django.db.models import Case, When, Avg, Count
    from django_redis import get_redis_connection

    redis = get_redis_connection("default")
    cart_item = None
    total_price = 0
    
    product = Product.objects.prefetch_related('reviews').annotate(
        average_rating=Avg("reviews__rating"),
        total_review_count=Count("reviews")
    ).get(pk=pk)

    product.average_rating = round(product.average_rating or 0, 1)

    rating_counts = {}
    for i in range(1, 6):
        rating_counts[i] = product.reviews.filter(rating=i).count()

    # Compute percentage (avoid division by zero)
    rating_percentages = {}
    for i in range(1, 6):
        rating_percentages[i] = ((rating_counts[i] / product.total_review_count * 100)
                                 if product.total_review_count else 0)

    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(
            customer=request.user,
            product=product
        ).first()

        cache_key = f"recent:{request.user.id}"

        last_key = f"last_view:{request.user.id}"
        last_product = redis.get(last_key)
        if last_product:
            last_product = int(last_product)
            if last_product != product.id:
                pair_key = f"coview:{last_product}"
                redis.zincrby(pair_key, 1, product.id)

        redis.setex(last_key, 60 * 30, product.id)  # 30 min window
    else:
        cache_key = f"recent:anon:{request.session.session_key}"
        if not request.session.session_key:
            request.session.save()

    if cart_item:
        total_price = product.price * cart_item.quantity

    recent_ids = cache.get(cache_key, [])
    if product.id in recent_ids:
        recent_ids.remove(product.id)

    recent_ids.insert(0, product.id)
    cache.set(cache_key, recent_ids, timeout=60 * 60 * 24 * 7)

    rec_key = f"coview:{product.id}"

    rec_ids = redis.zrevrange(rec_key, 0, 5)  # top 6
    rec_ids = [int(i) for i in rec_ids]
    
    recommended = Product.objects.filter(id__in=rec_ids)

    recently_viewed = (
        Product.objects
        .filter(id__in=recent_ids)
        .exclude(id=product.id)
    )

    preserved = Case(
        *[When(id=pk, then=pos) for pos, pk in enumerate(recent_ids)]
    )
    recently_viewed = recently_viewed.order_by(preserved)
    
    preserved_recom = Case(
        *[When(id=pk, then=pos) for pos, pk in enumerate(rec_ids)]
    )
    recommended = recommended.order_by(preserved_recom)

    context = {
        "product": product,
        "cart_item": cart_item,
        "total_price": total_price,
        "recently_viewed": recently_viewed,
        "recommended": recommended,
        "rating_counts": rating_counts,
        "rating_percentages": rating_percentages,
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
    from utils.constants import PaymentMethod, PaymentStatus
    user = request.user
    cart_items = Cart.objects.filter(customer=user)
    total = Cart.total_cart_price(user)
        
    shipping = round((Decimal(9 / 100) * total), 2)
    total_cost = (total + shipping)

    location = Location.objects.all()
    
    if request.method == "POST":
        shipping_address = request.POST.get("address")
        payment_method = request.POST.get("payment_method", "card")
        transport = request.POST.get("transport_option", "STANDARD")
        delivery_destination= request.POST.get("delivery_destination")
        upgrade_non_perishable_express = "upgrade_non_perishable_express" in request.POST

        
        order = process_order(shipping_address,payment_method,
                                       transport, delivery_destination,
                                       upgrade_non_perishable_express,
                                       request)
        
        if order.payment_method == PaymentMethod.PAY_ON_DELIVERY:
            try:
                reduce_stock_for_order(cart_items)
            except ValueError as e:
                messages.error(request, str(e))
                return redirect("farm:checkout")
            cart_items.delete()
            order.is_checkout_active = False
            order.status = PaymentStatus.PENDING
            order.save()
            return redirect("farm:all_products")
        
        return redirect("payment:servicepayment", order.pk)

    context = {
        "total": total,
        "shipping": shipping,
        "total_cost": total_cost,
        "delivery_type": cart_deliery_type(cart_items),
        "location": location
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
    This is farmers home page
    Contains activites which are only for farmers
    like uploading products
    """
    user = request.user
    city = "Mombasa"
    country = "kenya"
    start = get_default_range()

    if not request.user.has_perm("farm.view_product"):
        messages.error(request, _(f"You do not have permission to access "
                                  f"the page you requested."))
        return redirect(reverse_lazy("farm:home"))
    
    farms = user.farms.all()
    current_farmer_products = Product.objects.filter(farm__owner=user)

    order_items = (
        Order.objects
        .filter(items__product__farm__owner=user)
        .distinct()
        .order_by("-order_date")
        .prefetch_related("items__product")
    )

    order_items = (
        OrderItem.objects
        .filter(product__farm__owner=user)
        .select_related("order", "product")
        .order_by("-order__order_date")
    )

    for item in order_items:
        item.subtotal = item.quantity * item.product.price

    grouped_orders = []
    for order, items in groupby(order_items, key=attrgetter("order")):
        grouped_orders.append((order, list(items)))
    
    weather_data_list = weather_data(city, country)

    orders = (
        Order.objects
        .filter(items__product__farm__owner=user)
        .distinct()
        .order_by("-order_date")
    )

    total_sales_per_farmer = OrderItem.total_sales_per_farmer(user)

    inventory = Product.objects.filter(
        farm__owner=request.user,
        is_available=True
    )

    wallet_balance = OrderItem.wallet_balance_for_farmer(user)
    total_paid = Payout.total_paid(user)

    # KPI Cards
    total_revenue = OrderItem.total_revenue(user, start)
    orders_count = OrderItem.total_orders(user, start)
    total_units = OrderItem.total_units(user, start)

    current_order_count = orders_count.get("current_orders_count")
    lifetime_order_count = orders_count.get("lifetime")
    current_aov = round((total_revenue.get("current") / current_order_count if current_order_count else 0.00), 2)
    lifetime_aov = round((total_revenue.get("lifetime") / lifetime_order_count if lifetime_order_count else 0.00), 2)

    # Order Distribution
    order_distribution = OrderItem.order_distribution(user)
    # Sales Trend
    sales_trend = OrderItem.sales_timeseries(user)

    top_products = Product.objects.top_products(user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f"The product was saved successfuly")
            return redirect("farm:farmer_dashboard")
        else:
            return render(request, "farm/farmer_dashboard.html", {"form": form})
    
    form = ProductForm()
    new_farm_form = FarmForm()
    products_form = ProductForm(user=user)

    context = {
        "form": form,
        "farms": farms,
        "new_farm_form": new_farm_form,
        "products_form": products_form,

        "total_products": current_farmer_products.count(),
        "current_farmer_products": current_farmer_products,
        "grouped_orders": grouped_orders,
        "weather_data_list": weather_data_list,
        "total_orders": orders.count(),
        "total_sales_per_farmer": total_sales_per_farmer,
        "total_paid": total_paid,
        "inventory": inventory,
        "wallet_balance": wallet_balance,

        # KPI Cards
        "total_revenue": total_revenue,
        "orders_count": orders_count,
        "total_units": total_units,
        "aov": {
            "current_aov": current_aov,
            "lifetime_aov": lifetime_aov,
        },

        # Order Distribution
        "order_distribution": order_distribution,
        # Sales Trend
        "sales_trend": sales_trend,
        #Top products
        "top_products": top_products,
        }
    return render(request, "farm/farm/farmer_dashboard.html", context)

def create_or_edit_farm(request):
    user = request.user
    farms = user.farms.all()  # all farms owned by this user

    edit_form = None
    new_farm_form = FarmForm()  # form for creating new farm

    if request.method == "POST":
        # Determine if this is edit or create form
        if "farm_id" in request.POST:  # editing existing farm
            farm_id = request.POST.get("farm_id")
            try:
                farm = farms.get(id=farm_id)
            except Farm.DoesNotExist:
                messages.error(request, "Invalid farm selected.")
                return redirect("farm:farmer_dashboard")
            
            edit_form = FarmForm(request.POST, request.FILES, instance=farm)
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, f"Farm '{farm.name}' updated!")
                return redirect("farm:farmer_dashboard")
        
        else:  # creating new farm
            new_farm_form = FarmForm(request.POST, request.FILES)
            if new_farm_form.is_valid():
                new_farm = new_farm_form.save(commit=False)
                new_farm.owner = user
                new_farm.save()
                assign_hub_to_farm(new_farm)
                messages.success(request, f"New farm '{new_farm.name}' created!")
                return redirect("farm:farmer_dashboard")
            

    context = {
        "farms": farms,
        "edit_form": edit_form,
        "new_farm_form": new_farm_form,
    }
    return render(request, "farm/dashboard.html", context)


def create_product(request):
    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES)
        if product_form.is_valid():
            new_product = product_form.save(commit=False)
            farm = product_form.cleaned_data.get("farm")
            new_product.hub = farm.hub

            new_product.save()
            messages.success(request, _("New product created successfully"))
            return redirect("farm:farmer_dashboard")
    else:
        pass

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


def hubs_by_county(request):
    from farm.models import Hub
    county = request.GET.get("county")
    hubs = Hub.objects.filter(location__name=county).values("id", "name")
    return JsonResponse(list(hubs), safe=False)

