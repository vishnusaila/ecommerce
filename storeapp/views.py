from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, OrderItem
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
import razorpay

User = get_user_model()

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.exclude(pk=pk)[:4]
    return render(request, 'product_detail.html', {'product': product, 'related_products': related_products})

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
        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

def update_cart(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        new_cart = {}
        for key in list(cart.keys()):
            qty_key = f'qty_{key}'
            remove_key = f'remove_{key}'
            if remove_key in request.POST:
                continue
            if qty_key in request.POST:
                try:
                    qty = int(request.POST[qty_key])
                    if qty > 0:
                        new_cart[key] = qty
                except:
                    continue
        request.session['cart'] = new_cart
    return redirect('cart_view')

def checkout(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = []
    total = 0
    for product in products:
        quantity = cart[str(product.id)]
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
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

def razorpay_checkout(request):
    cart = request.session.get('cart', {})
    total = 0
    valid_cart = {}
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(id=pid)
            total += product.price * qty
            valid_cart[pid] = qty
        except Product.DoesNotExist:
            continue
    request.session['cart'] = valid_cart
    if not valid_cart:
        return redirect('cart_view')
    amount_paise = int(total * 100)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({'amount': amount_paise, 'currency': 'INR', 'payment_capture': '1'})
    return render(request, 'store/payment.html', {'payment': payment, 'key': settings.RAZORPAY_KEY_ID, 'total': total})

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registration_success')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

def custom_login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
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

@login_required
def profile_view(request):
    orders = Order.objects.filter(name=request.user.username).order_by('-id')
    return render(request, 'store/profile.html', {'orders': orders})
