from django.db import transaction
from django.utils.translation import gettext as _

from ..models import Product

def reduce_stock_for_order(cart_items):
    """
    Safely reduce stock for all items in an order.
    Parameters:
        cart_items (iterable): items with `.product` and `.quantity`
    Raises:
        ValueError: if any product has insufficient stock
    """
    with transaction.atomic():
        product_ids = [item.product_id for item in cart_items]
        products = Product.objects.select_for_update().filter(pk__in=product_ids)
        product_map = {p.pk: p for p in products}

        for item in cart_items:
            product = product_map.get(item.product_id)
            if not product:
                raise ValueError(_(f"Product {item.product.name} does not exist"))
            if product.quantity < item.quantity:
                raise ValueError(_(f"Not enought stock for {product.name}"))
            
        for item in cart_items:
            product = product_map[item.product_id]
            product.quantity -= item.quantity

        Product.objects.bulk_update(products, {"quantity"})


