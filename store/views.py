from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterForm
from django.db.models import Q
from .models import Product, Category, Order, OrderItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
import requests
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages

# Create your views here.

        #THE VIEW PAGE
def home(request):
    products = Product.objects.all()
    return render(request, "index.html", {
        "products": products
    })
    
def shop(request):
    query = request.GET.get("q")
    
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
     products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "shop.html", {
        "products": products,
        "categories": categories
        
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, "product_detail.html", {
        "product": product
    })
    
def about(request):
    products = Product.objects.all()
    return render(request, "about.html", {
        "products": products
    })
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if name and email and subject and message:
            # Option 1: Send an email (requires email setup in settings.py)
            send_mail(
                f"{subject} - from {name}",
                message,
                email,
                ['ichadominic5@gmail.com'],  # Replace with your email
            )
            messages.success(request, "Message sent successfully!")
            return redirect('contact')
        else:
            messages.error(request, "Please fill in all fields.")

    return render(request, 'contact.html')
    #   END VIEW
    
    # LOGIN/ AUTHENTICATION
    
def register(request):

    if request.method == "POST":

        form =form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("login")

    else:
        form = RegisterForm()

    return render(request, "register.html", {
        "form": form
    })
    #   END AUTH
    
    # ADDING TO CART
def add_to_cart(request, id):

    cart = request.session.get("cart", {})

    if str(id) in cart:
        cart[str(id)] += 1
    else:
        cart[str(id)] = 1

    request.session["cart"] = cart
    
    messages.success(request, "Product added to cart successfully!")

    return redirect("shop")

            # CART-VIEW
def cart_view(request):

    cart = request.session.get("cart", {})

    products = []
    total = 0

    for product_id, quantity in cart.items():

        product = Product.objects.get(id=product_id)

        product.quantity = quantity
        product.subtotal = product.price * quantity

        total += product.subtotal

        products.append(product)

    return render(request, "cart.html", {
        "products": products,
        "total": total
    })
    


@login_required
def update_cart_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__user=request.user)
    action = request.POST.get("action")

    if action == "increase":
        item.quantity += 1
    elif action == "decrease" and item.quantity > 1:
        item.quantity -= 1

    item.save()
    return redirect("cart")  # Redirect back to your cart page
    
            # REMOVE FROM CART
def remove_from_cart(request, id):

    cart = request.session.get("cart", {})

    if str(id) in cart:
        del cart[str(id)]

    request.session["cart"] = cart

    return redirect("cart")

    # END CART
    
    # Create Checkout View
@login_required
def checkout(request):

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("shop")

    total = 0
    products = []

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        product.quantity = quantity
        product.subtotal = product.price * quantity
        total += product.subtotal
        products.append(product)

    return render(request, "checkout.html", {
        "products": products,
        "total": total
    })
    
    # paystack payment
@login_required
def initiate_payment(request):

    cart = request.session.get("cart", {})

    if not cart:
        return redirect("shop")

    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        total += product.price * quantity

    # Create order (not completed yet)
    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        is_completed=False
    )

    headers = {
    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json"
}

    usd_to_naira_rate = Decimal("1500")  # use Decimal, not float
    naira_total = total * usd_to_naira_rate

    amount = int(naira_total * 100)  # convert to kobo

    data = {
    "email": request.user.email or "test@email.com",
    "amount": amount,   # ✅ USE converted amount
    "reference": f"ORDER_{order.id}",
    "callback_url": "http://nickdev.co.site/verify-payment/"
}

    response = requests.post(
        "https://api.paystack.co/transaction/initialize",
        json=data,
        headers=headers
    )

    response_data = response.json()
    print(response_data)

    if response_data["status"]:
        order.reference = response_data["data"]["reference"]
        order.save()
        return redirect(response_data["data"]["authorization_url"])

    return redirect("cart")

        

@login_required
def verify_payment(request):

    reference = request.GET.get("reference")

    if not reference:
        return render(request, "payment_failed.html")

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(
        f"https://api.paystack.co/transaction/verify/{reference}",
        headers=headers
    )

    response_data = response.json()
    print(response_data)

    if response_data.get("data") and response_data["data"]["status"] == "success":

        try:
            order = Order.objects.get(reference=reference)
            order.is_completed = True
            order.save()
            request.session["cart"] = {}
            return render(request, "payment_success.html", {"order": order})
        except Order.DoesNotExist:
            return render(request, "payment_failed.html")

    return render(request, "payment_failed.html")

        # payment end
        
