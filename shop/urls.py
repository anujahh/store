# shop/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    path('login/', views.login_register_view, name='login_register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    path('saved-dates/', views.saved_dates_view, name='saved_dates_view'),
    path('saved-dates/add/', views.add_saved_date, name='add_saved_date'),
    path('saved-dates/delete/<int:date_id>/', views.delete_saved_date, name='delete_saved_date'),
    
    path('orders/', views.order_history, name='order_history'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
]