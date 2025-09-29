from decimal import Decimal
from .models import Product, ProductSizeVariant

class SessionCart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, variant_id, qty=1):
        """Add a product variant to the cart or update quantity"""
        key = str(variant_id)
        if key in self.cart:
            self.cart[key]['qty'] += qty
        else:
            variant = ProductSizeVariant.objects.select_related('product', 'size').get(pk=variant_id)
            self.cart[key] = {
                'variant_id': variant.id,
                'product_id': variant.product.id,
                'qty': qty,
            }
        self.save()

    def update(self, variant_id, qty):
        """Update the quantity of a cart item"""
        key = str(variant_id)
        if key in self.cart:
            if qty <= 0:
                self.remove(variant_id)
            else:
                self.cart[key]['qty'] = qty
            self.save()

    def remove(self, variant_id):
        """Remove an item from the cart"""
        key = str(variant_id)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def clear(self):
        """Empty the cart"""
        self.cart = {}
        self.save()

    def save(self):
        """Mark session as modified"""
        self.session['cart'] = self.cart
        self.session.modified = True

    def items(self):
        """Yield full item data including variant and product objects"""
        variant_ids = [int(k) for k in self.cart.keys()]
        variants = ProductSizeVariant.objects.select_related('product', 'size').filter(id__in=variant_ids)
        variants_map = {v.id: v for v in variants}

        for variant_id_str, item in self.cart.items():
            variant_id = int(variant_id_str)
            variant = variants_map.get(variant_id)
            if not variant:
                continue

            yield {
                'variant': variant,
                'product': variant.product,
                'size': variant.size.name,
                'price': variant.product.price,
                'qty': item['qty'],
                'total_price': variant.product.price * item['qty'],
                'image': variant.product.image.url if variant.product.image else '',
            }

    def total(self):
        """Compute total price of cart"""
        return sum(item['price'] * item['qty'] for item in self.items())

    def __iter__(self):
        return self.items()
