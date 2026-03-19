from django.urls import path
from . import views

urlpatterns = [
    # Basic Pages
    path('', views.home, name='home'),
    path('product/<int:pk>/',
          views.product_detail,
            name='product_detail'),
    path('search/', views.search, name='search'),
    
    # Cart System
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('update_item/', views.update_item, name="update_item"),

    # Checkout & Payment (Fixes Applied)
    # Ye page dikhayega summary
    path('checkout/<int:pk>/', views.checkout, name='checkout'), 
    
    # Ye Stripe payment start karega (Iska naam 'create_checkout_session' hi rakha hai)
    path('create-checkout-session/<int:pk>/', views.create_checkout_session, name='create_checkout_session'),
    
    # Success aur Cancel pages
    path('payment_success/', views.payment_success_view, name='payment_success'),
    path('payment_cancel/', views.payment_cancel_view, name='payment_cancel'),

    # Dashboard & Auth
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
# urls.py mein ye line check karein
path('my-orders/', views.orders_view, name='orders_view'),
]