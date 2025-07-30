from django.contrib import admin
from .models import Product, Order, OrderItem

# ✅ Custom admin display for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']
    list_filter = ['price']

# ✅ Register models with custom admin
admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
