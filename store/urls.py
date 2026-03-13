from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView, LoginView

urlpatterns = [
    path("", views.home, name="index"),
    path("shop", views.shop, name="shop"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("add-to-cart/<int:id>/", views.add_to_cart, name="add_to_cart"),
    path("remove-from-cart/<int:id>/", views.remove_from_cart, name="remove_from_cart"),
    path('checkout/', views.checkout, name="checkout"),
    path("pay/", views.initiate_payment, name="initiate_payment"),
    path("verify-payment/", views.verify_payment, name="verify_payment"),
    path("cart/update/<int:item_id>/", views.update_cart_quantity, name="update_cart_quantity"),
    
    # LOGIN / AUTHENTICATION
    path('register/', views.register, name="register"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

]