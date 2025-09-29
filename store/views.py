from itertools import product
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from .models import Category, Product, ProductSizeVariant, SubCategory, Order, OrderItem
from .cart import SessionCart
from .forms import CheckoutForm
from django.urls import reverse
from django.conf import settings
import stripe
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

def product_list(request, category_slug=None, sub_slug=None):
    categories = Category.objects.all()
    products = Product.objects.filter(active=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    if sub_slug:
        sub = get_object_or_404(SubCategory, slug=sub_slug, category=category)
        products = products.filter(subcategory=sub)
    return render(request, 'store/product_list.html', {'products': products, 'categories': categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, active=True)
    variants = product.variants.select_related('size')
    return render(request, 'store/product_detail.html', {'product': product, 'variants': variants})

# AJAX cart endpoints
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
def ajax_add_to_cart(request):
    variant_id = request.POST.get('variant_id')
    qty = int(request.POST.get('qty', 1))
    if not variant_id:
        return JsonResponse({'error':'no variant id'}, status=400)
    cart = SessionCart(request)
    try:
        cart.add(variant_id=int(variant_id), qty=qty)
    except ProductSizeVariant.DoesNotExist:
        return JsonResponse({'error':'invalid variant'}, status=400)
    return JsonResponse({'success': True, 'cart_total': str(cart.total())})

@require_POST
def ajax_update_cart(request):
    variant_id = request.POST.get('variant_id')
    qty = int(request.POST.get('qty', 1))
    cart = SessionCart(request)
    cart.update(variant_id=int(variant_id), qty=qty)
    return JsonResponse({'success': True, 'cart_total': str(cart.total())})

@require_POST
def ajax_remove_from_cart(request):
    variant_id = request.POST.get('variant_id')
    cart = SessionCart(request)
    cart.remove(variant_id=int(variant_id))
    return JsonResponse({'success': True, 'cart_total': str(cart.total())})

def view_cart(request):
    cart = SessionCart(request)
    items = list(cart.items())
    return render(request, 'store/cart.html', {'items': items, 'cart_total': cart.total()})

# Checkout
def checkout(request):
    cart = SessionCart(request)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method", "COD")  # COD or CARD

        if not mobile:
            messages.error(request, "Mobile number is required.")
            return redirect("store:checkout")

        # Create Order
        order = Order.objects.create(
            customer_name=name,
            email=email,
            mobile=mobile,
            address=address,
            payment_method=payment_method,
            paid=(payment_method == "COD"),  # COD marked paid=False by default
        )

        # Create OrderItems
        for item in cart.items():
            variant = ProductSizeVariant.objects.get(pk=item["variant_id"])
            OrderItem.objects.create(
                order=order,
                variant=variant,
                product=variant.product,
                size=item["size"],
                price=variant.product.price,
                qty=item["qty"],
            )

        # Clear cart
        cart.clear()

        # Payment handling
        if payment_method == "CARD":
            # Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(order.get_total_cost() * 100),  # in cents
                currency="usd",
                metadata={"order_id": order.id},
            )
            order.stripe_payment_intent = intent.id
            order.save()

            return render(request, "store/checkout_payment.html", {
                "order": order,
                "client_secret": intent.client_secret,
                "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            })
        else:  # COD
            return render(request, "store/checkout_success.html", {"order": order})

    # GET request
    return render(request, "store/checkout.html", {"cart_items": cart.items(), "cart_total": cart.total()})

# -----------------------------
# Stripe Webhook
# -----------------------------
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        order_id = payment_intent.get("metadata", {}).get("order_id")
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.paid = True
                order.save()
            except Order.DoesNotExist:
                pass

    return HttpResponse(status=200)

# -----------------------------
# Checkout Success & Cancel Pages
# -----------------------------
def checkout_success(request):
    return render(request, "store/checkout_success.html")

def checkout_cancel(request):
    return render(request, "store/checkout_cancel.html")





