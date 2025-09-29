from django.contrib import admin
from .models import Order, OrderItem, Product, ProductSizeVariant, Category, SubCategory, Size

# --- Inline OrderItem inside Order admin ---
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'size', 'price', 'qty')
    can_delete = True

# --- Order admin ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'mobile', 'payment_method', 'paid', 'created_at')
    list_filter = ('paid', 'payment_method', 'created_at')
    search_fields = ('customer_name', 'mobile', 'email')
    inlines = [OrderItemInline]
    readonly_fields = ('stripe_payment_intent',)
    ordering = ('-created_at',)

    # Optional admin actions
    actions = ['mark_as_paid', 'mark_as_unpaid']

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(paid=True)
        self.message_user(request, f"{updated} order(s) marked as paid.")
    mark_as_paid.short_description = "Mark selected orders as paid"

    def mark_as_unpaid(self, request, queryset):
        updated = queryset.update(paid=False)
        self.message_user(request, f"{updated} order(s) marked as unpaid.")
    mark_as_unpaid.short_description = "Mark selected orders as unpaid"

# --- Product admin ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'subcategory', 'price', 'active', 'created_at')
    list_filter = ('category', 'subcategory', 'active')
    search_fields = ('title',)

# --- ProductSizeVariant admin ---
@admin.register(ProductSizeVariant)
class ProductSizeVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'stock')
    list_filter = ('product__category', 'size')
    search_fields = ('product__title',)

# --- Category admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

# --- SubCategory admin ---
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}

# --- Size admin ---
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
