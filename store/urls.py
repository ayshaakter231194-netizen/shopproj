from django.urls import path
from . import views

app_name = 'store'
urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('category/<slug:category_slug>/<slug:sub_slug>/', views.product_list, name='product_list_by_sub'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('ajax/cart/add/', views.ajax_add_to_cart, name='ajax_add_to_cart'),
    path('ajax/cart/update/', views.ajax_update_cart, name='ajax_update_cart'),
    path('ajax/cart/remove/', views.ajax_remove_from_cart, name='ajax_remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]
