from django.shortcuts import render

# Create your views here.
# shop/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Product, Category, Review, Wishlist, SavedDate, Order, OrderItem, UserProfile
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
import json
from decimal import Decimal

# --- Home & Product Views ---
def home(request):
    featured_products = Product.objects.all().order_by('-id')[:8] # Get 8 latest products
    return render(request, 'shop/index.html', {'featured_products': featured_products})

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, 'shop/products.html', {'products': products, 'categories': categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    # Add review form logic here if needed
    return render(request, 'shop/product_detail.html', {'product': product, 'reviews': reviews})

# --- Authentication ---
def login_register_view(request):
    if request.method == 'POST':
        # Check which form was submitted
        if 'register' in request.POST:
            reg_form = UserCreationForm(request.POST)
            if reg_form.is_valid():
                user = reg_form.save()
                login(request, user)
                messages.success(request, 'Registration successful. You are now logged in.')
                return redirect('home')
        elif 'login' in request.POST:
            auth_form = AuthenticationForm(request, data=request.POST)
            if auth_form.is_valid():
                user = auth_form.get_user()
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
    
    reg_form = UserCreationForm()
    auth_form = AuthenticationForm()
    return render(request, 'shop/login_register.html', {'reg_form': reg_form, 'auth_form': auth_form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('home')

# --- Cart Functionality ---
@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    cart_items = []
    total_price = 0
    for product in products:
        quantity = cart[str(product.id)]
        item_total = product.price * quantity
        cart_items.append({'product': product, 'quantity': quantity, 'total': item_total})
        total_price += item_total
    
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return JsonResponse({'status': 'success', 'message': f'{product.name} added to cart'})

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, 'Item removed from cart.')
    return redirect('cart_view')

# --- Wishlist ---
@login_required
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'shop/wishlist.html', {'wishlist': wishlist})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    messages.success(request, f'{product.name} added to your wishlist.')
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = Wishlist.objects.get(user=request.user)
    wishlist.products.remove(product)
    messages.success(request, f'{product.name} removed from your wishlist.')
    return redirect('wishlist_view')

# --- Saved Dates ---
@login_required
def saved_dates_view(request):
    dates = SavedDate.objects.filter(user=request.user).order_by('event_date')
    return render(request, 'shop/saved_dates.html', {'dates': dates})

@login_required
@require_POST
def add_saved_date(request):
    event_name = request.POST.get('event_name')
    event_date = request.POST.get('event_date')
    if event_name and event_date:
        SavedDate.objects.create(user=request.user, event_name=event_name, event_date=event_date)
        messages.success(request, 'Date saved successfully!')
    else:
        messages.error(request, 'Please provide both an event name and a date.')
    return redirect('saved_dates_view')

@login_required
def delete_saved_date(request, date_id):
    date = get_object_or_404(SavedDate, id=date_id, user=request.user)
    date.delete()
    messages.success(request, 'Saved date removed.')
    return redirect('saved_dates_view')

# --- Orders & Payment ---
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user, is_paid=True).order_by('-created_at')
    return render(request, 'shop/orders.html', {'orders': orders})

@login_required
def checkout(request):
    # This view will just render the page with the PayPal button.
    # The actual processing happens on the client-side and is verified in process_payment.
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart_view')
        
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)
    total_price = sum(p.price * cart[str(p.id)] for p in products)
    
    user_profile = UserProfile.objects.get(user=request.user)
    
    # Simple token logic: 1 token = $1 discount
    tokens_to_use = int(request.GET.get('tokens', 0))
    if tokens_to_use > user_profile.tokens:
        tokens_to_use = user_profile.tokens
        
    discount = Decimal(tokens_to_use)
    final_price = total_price - discount
    if final_price < 0:
        final_price = 0

    return render(request, 'shop/checkout.html', {
        'total_price': total_price,
        'user_tokens': user_profile.tokens,
        'tokens_to_use': tokens_to_use,
        'discount': discount,
        'final_price': final_price
    })

@login_required
@require_POST
def process_payment(request):
    try:
        data = json.loads(request.body)
        transaction_id = data['transaction_id']
        amount_paid = Decimal(data['amount_paid'])
        tokens_used = int(data.get('tokens_used', 0))

        cart = request.session.get('cart', {})
        if not cart:
            return JsonResponse({'error': 'Cart is empty'}, status=400)
        
        # Create Order
        order = Order.objects.create(
            user=request.user, 
            total_paid=amount_paid,
            is_paid=True,
            paypal_transaction_id=transaction_id
        )

        # Create OrderItems
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
        
        # Handle tokens
        user_profile = UserProfile.objects.get(user=request.user)
        # Deduct used tokens
        user_profile.tokens -= tokens_used
        # Award new tokens (e.g., 1 token for every $10 spent)
        new_tokens_earned = int(amount_paid // 10)
        user_profile.tokens += new_tokens_earned
        user_profile.save()

        # Clear the cart
        request.session['cart'] = {}

        messages.success(request, f'Payment successful! You earned {new_tokens_earned} tokens.')
        return JsonResponse({'status': 'success', 'redirect_url': '/payment-success/'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def payment_success(request):
    return render(request, 'shop/payment_success.html')

def payment_cancelled(request):
    return render(request, 'shop/payment_cancelled.html')

def about_us_view(request):
    return render(request, 'shop/about.html')