from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
from django.contrib.auth import logout
from django.conf import settings
import razorpay
from storeapp.models import Product
# -------------------------
# Home Page
# -------------------------
def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

# -------------------------
# Product Detail Page
# -------------------------
from django.shortcuts import render, get_object_or_404
from .models import Product

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.exclude(pk=pk)[:4]  # show any 4 other products
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products
    })


# -------------------------
# Cart Functions
# -------------------------
def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    return redirect('cart_view')

def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0

    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        new_cart = {}

        for key in list(cart.keys()):
            qty_key = f'qty_{key}'
            remove_key = f'remove_{key}'

            if remove_key in request.POST:
                continue  # remove item

            if qty_key in request.POST:
                try:
                    qty = int(request.POST[qty_key])
                    if qty > 0:
                        new_cart[key] = qty
                except:
                    continue

        request.session['cart'] = new_cart
    return redirect('cart_view')

# -------------------------
# Checkout Page
# -------------------------
def checkout(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0

    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        order = Order.objects.create(name=name, address=address, phone=phone)

        for item in cart_items:
            OrderItem.objects.create(order=order, product=item['product'], quantity=item['quantity'])

        request.session['cart'] = {}
        return render(request, 'store/thankyou.html', {'name': name})

    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})

# -------------------------
# Razorpay Payment Integration
# -------------------------
from django.shortcuts import render, get_object_or_404, redirect
import razorpay
from .models import Product
from django.conf import settings

def razorpay_checkout(request):
    cart = request.session.get('cart', {})
    total = 0

    # Clean cart if any product doesn't exist
    valid_cart = {}
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(id=pid)
            total += product.price * qty
            valid_cart[pid] = qty
        except Product.DoesNotExist:
            continue  # Skip deleted products

    # Update session cart with valid items only
    request.session['cart'] = valid_cart

    # If cart is empty after cleaning
    if not valid_cart:
        return redirect('cart_view')  # or render a message: "Cart is empty"

    # Convert total to paise
    amount_paise = int(total * 100)

    # Create Razorpay order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({'amount': amount_paise, 'currency': 'INR', 'payment_capture': '1'})

    return render(request, 'store/payment.html', {
        'payment': payment,
        'key': settings.RAZORPAY_KEY_ID,
        'total': total
    })


# -------------------------
# Logout View
# -------------------------
def logout_view(request):
    logout(request)
    return redirect('home')

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registration_success')  # 👈 redirect after saving
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})



from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages

User = get_user_model()

def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')  # or any success page
        else:
            # If user doesn't exist, create and log them in
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                messages.success(request, "Registered and logged in successfully!")
                return redirect('home')
            else:
                messages.error(request, "Incorrect password. Please try again.")
    
    return render(request, 'login.html')


def registration_success(request):
    return render(request, 'store/registration_success.html')




from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def profile_view(request):
    orders = Order.objects.filter(name=request.user.username).order_by('-id')
    return render(request, 'store/profile.html', {'orders': orders})

