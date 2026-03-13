from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):

    name = models.CharField(max_length=100)
    
class Product(models.Model):
    
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True
    )
    name = models.CharField(max_length=200)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    description = models.TextField()

    image = models.ImageField(upload_to="products/")

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    from django.contrib.auth.models import User
    
""" Order & Checkout System. """

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    reference = models.CharField(max_length=200, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order {self.id}"

    def save(self, *args, **kwargs):
        # Ensure a unique reference exists for Paystack
        if not self.reference:
            import uuid
            self.reference = uuid.uuid4().hex
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"