# shop/admin.py

from django.contrib import admin
from .models import UserProfile, Category, Product, Review, Wishlist, SavedDate, Order, OrderItem

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'collection', 'price', 'stock')
    prepopulated_fields = {'slug': ('name',)}

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'is_paid', 'total_paid')
    list_filter = ('is_paid', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(UserProfile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(SavedDate)
admin.site.register(Order, OrderAdmin)