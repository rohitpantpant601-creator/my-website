from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from .models import Product, Cart, CartItem, Order, OrderItem, Seller
import stripe
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Cart, CartItem 
from django.shortcuts import redirect, render
from django.shortcuts import render, redirect
from .forms import CheckoutForm




# Stripe API Key (Use your Secret Key from Dashboard)
stripe.api_key = "sk_test_51T5ej7GbD9lCq6Nt8hLCGHUQnxAlJhiQYfVMZVBtCU5IYMXTRg9rltKyAfqagDB1mCrgOV7HQwlY8OJhWfP57X4K00uuOC5CCF"

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')  # 'login' aapke login URL ka name hona chahiye
def create_checkout_session(request, pk):
    # 1. Product toh humesha hoga hi
    product = get_object_or_404(Product, pk=pk)
    
    # 2. Cart logic with fallback (Try-Except)
    try:
        # Check karte hain ki kya user ke cart mein ye product pehle se hai?
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, product=product)
        quantity = cart_item.quantity  # Agar mil gaya toh cart wali quantity
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        # Agar cart empty hai ya product cart mein nahi hai, toh default 1 quantity
        quantity = 1 

    # 3. Price calculation (Paise mein)
    unit_amount_in_paise = int(product.price * 100)

    # 4. Stripe Session
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card',],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': unit_amount_in_paise,
            },
            'quantity': quantity,
        }],
        mode='payment',
        # Tip: Ngrok use kar rahe ho toh success_url mein hardcoded IP ki jagah request.build_absolute_uri use kar sakte ho
        success_url='http://127.0.0.1:8000/success/',
        cancel_url='http://127.0.0.1:8000/cancel/',
    )
    pass
    
    return redirect(checkout_session.url, code=303)

def checkout_view(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save() # Data Database mein save ho gaya
            
            # Logic for Redirection
            if order.payment_method == 'ONLINE':
                # Stripe Session Create Karein
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {'name': 'Decathlon Product'},
                            'unit_amount': int(order.amount * 100), # Amount in paise
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url='http://127.0.0.1:8000/success/',
                    cancel_url='http://127.0.0.1:8000/cancel/',
                )
                return redirect(session.url, code=303)
            
            else:
                # Agar COD hai toh seedha Success page
                return redirect('order_success')
    else:
        form = CheckoutForm()
    
    return render(request, 'checkout.html', {'form': form})


@login_required
def orders_view(request):
    # 'payment_status' ki jagah 'paid' use karein kyunki model mein wahi hai
    orders = Order.objects.filter(
        user=request.user, 
        paid=True  # Yahan badlao kiya gaya hai
    ).prefetch_related('items').order_by('-created_at')
    
    return render(request, 'order.html', {'orders': orders})

@login_required
def checkout(request, pk):
    print(f"DEBUG: Checkout page for product ID: {pk}") # Ye terminal mein ID print karega
    product = get_object_or_404(Product, pk=pk)
    # ... baaki code
    total_price = product.price
    
    if request.method == 'POST':
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {'name': product.name},
                        'unit_amount': int(total_price * 100), # Amount in Paise
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://127.0.0.1:8000/success/',
                cancel_url='http://127.0.0.1:8000/cancel/',
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            print(f"STRIPE ERROR: {e}")
            return render(request, 'checkout.html', {'error': str(e), 'product': product, 'total': total_price})

    return render(request, 'checkout.html', {'product': product, 'total': total_price})


@login_required
def checkout(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    quantity = 1
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
    elif request.GET.get('quantity'):
        quantity = int(request.GET.get('quantity'))

    total_price = product.price * quantity

    if request.method == 'POST':
        try:
            # Stripe Checkout Session create karein
            checkout_session = stripe.checkout.Session.create(
                # 'card' ki jagah niche wali line use karein dashboard settings uthane ke liye
                payment_method_types=['card'], 
                # Google Pay enable karne ke liye dashboard mein settings on honi chahiye
                # Aur code mein hum automatic methods ka option de sakte hain agar aap 
                # modern API use kar rahe hain, par Checkout Session mein niche wala setup best hai:
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': product.name,
                        },
                        'unit_amount': int(total_price * 100), 
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://127.0.0.1:8000/success/',
                cancel_url='http://127.0.0.1:8000/cancel/',
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return render(request, 'checkout.html', {'error': str(e), 'product': product, 'total': total_price})

    return render(request, 'checkout.html', {
        'product': product, 
        'total': total_price, 
        'quantity': quantity
    })



def payment_cancel_view(request):
    return render(request, 'payment_cancel.html')
def payment_success_view(request):
    # Payment ke baad cart khali karna (Optional logic)
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart.cartitem_set.all().delete()
    return render(request, 'payment_success.html')




    

def home(request):
    products = Product.objects.all()
    # Base template ki jagah home template render karein jo base ko extend kare
    return render(request, 'home.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products.html', {'product': product})

def search(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        products = Product.objects.all()
    return render(request, 'search.html', {'products': products, 'query': query})

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    # URL name use karein, path nahi
    return redirect('cart') 
@login_required
def cart(request):
    # 1. Get or create the cart for the current user
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # 2. Use the correct reverse lookup name (case-sensitive)
    # If your model is "CartItem", the default is "cartitem_set"
    items = cart.items.all()
    
    # 3. Calculate total safely
    # We use a generator expression to sum the prices
    total = sum(item.product.price * item.quantity for item in items)
    
    return render(request, 'cart.html', {
        'items': items, 
        'total': total,
        'cart': cart # Useful to pass the cart object itself too
    })
@login_required
def checkout(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    quantity = 1
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
    elif request.GET.get('quantity'):
        quantity = int(request.GET.get('quantity'))

    total_price = product.price * quantity

    if request.method == 'POST':
        try:
            # Stripe Checkout Session create karein
            checkout_session = stripe.checkout.Session.create(
                # 'card' ki jagah niche wali line use karein dashboard settings uthane ke liye
                payment_method_types=['card'], 
                # Google Pay enable karne ke liye dashboard mein settings on honi chahiye
                # Aur code mein hum automatic methods ka option de sakte hain agar aap 
                # modern API use kar rahe hain, par Checkout Session mein niche wala setup best hai:
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': product.name,
                        },
                        'unit_amount': int(total_price * 100), 
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://127.0.0.1:8000/success/',
                cancel_url='http://127.0.0.1:8000/cancel/',
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return render(request, 'checkout.html', {'error': str(e), 'product': product, 'total': total_price})

    return render(request, 'checkout.html', {
        'product': product, 
        'total': total_price, 
        'quantity': quantity
    })
    
@login_required
def seller_dashboard(request):
    # Check karein agar user seller hai
    try:
        seller = request.user.seller
        products = Product.objects.filter(seller=seller)
        return render(request, 'seller_dashboard.html', {'products': products})
    except Seller.DoesNotExist:
        return redirect('home')

# --- AUTHENTICATION ---

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'Ragister.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')
@login_required
def buy_now(request, product_id): 
    # Neeche line 201 mein bhi pk ko product_id kar do
    product = get_object_or_404(Product, pk=product_id) 
    
    return render(request, 'checkout.html', {'product': product})
@csrf_exempt
@login_required
def update_item(request):
    try:
        data = json.loads(request.body)
        productId = data.get('productId')
        action = data.get('action')

        cart, created = Cart.objects.get_or_create(user=request.user)
        product = Product.objects.get(id=productId)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if action == 'add':
            cart_item.quantity += 1
        elif action == 'remove':
            cart_item.quantity -= 1
        elif action == 'delete':  # Ye nayi line poora product hata degi
            cart_item.quantity = 0
# Action ke baad hamesha save karein
        cart_item.save()

        # Agar quantity 0 ya usse kam hai toh item ko cart se hata dein
        if cart_item.quantity <= 0:
            cart_item.delete()

        return JsonResponse('Item was updated', safe=False)

    except Exception as e:
        print(f"ERROR: {e}")
        return JsonResponse({'error': str(e)}, status=400)
    
    # 'pk' ko function ke brackets mein add karein

    # Ab aap is 'pk' ka use karke product ya order fetch kar sakte hain
    # Example: product = Product.objects.get(id=pk)
    
 