from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart_view'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),

    # Auth
    path('login/', views.custom_login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('razorpay/checkout/', views.razorpay_checkout, name='razorpay_checkout'),
    path('register/', views.register_view, name='register'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('profile/', views.profile_view, name='profile'),



]



