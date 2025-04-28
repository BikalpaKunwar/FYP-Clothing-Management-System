from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)
    role = models.CharField(max_length=50)

    def __str__(self):
        return str(self.customer_id)


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('hoodie', 'Hoodie'),
        ('tshirt', 'T-Shirt'),
        ('trouser', 'Trouser'),
        ('sweatshirt', 'Sweatshirt'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name


class Bid(models.Model):
    bid_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.CharField(max_length=50)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')
    ], default='pending')

    def __str__(self):
        return f"Bid {self.bid_id} - {self.product.product_name}"


from django.contrib.auth import get_user_model
User = get_user_model()

class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('eSewa', 'eSewa'),
        ('COD', 'Cash on Delivery'),
    ]

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], default='pending')

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='COD'  # ✅ Default is Cash on Delivery if not chosen
    )

    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.order_id} - {self.product.product_name}"





class Rating(models.Model):
    rating_id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=50)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} for {self.product.product_name}"


class Chat(models.Model):
    chat_id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=50)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.chat_id} by {self.user}"


class Coupon(models.Model):
    coupon_id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=50)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    coupon_code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    expiry_date = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Coupon {self.coupon_code}"


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ❤️ {self.product.product_name}"



class ContactMessage(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.email}"


