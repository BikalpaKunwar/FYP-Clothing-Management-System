from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.contrib.auth.models import User as DjangoUser
from .forms import CustomUserRegistrationForm, LoginForm, ProductForm
from .models import Product, CartItem, WishlistItem, Order



User = get_user_model()


# ---------- PUBLIC ----------
def home(request):
    return render(request, 'mytemplates/home.html')

def aboutus(request):
    return render(request, 'mytemplates/aboutus.html')


def contact(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact')
        message = request.POST.get('message')

        if full_name and email and contact_number and message:
            ContactMessage.objects.create(
                full_name=full_name,
                email=email,
                contact=contact_number,
                message=message
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
        else:
            messages.error(request, "Please fill out all the fields.")

    return render(request, 'mytemplates/contact.html')




def forgotpassword(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            users = User.objects.filter(email=email)
            if users.exists():
                for user in users:
                    subject = "Password Reset - Bonapapa"
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = default_token_generator.make_token(user)
                    reset_url = request.build_absolute_uri(
                        reverse_lazy('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                    )
                    message = f"Hi {user.username},\n\nClick the link below to reset your password:\n{reset_url}"
                    send_mail(subject, message, 'noreply@bonapapa.com', [user.email])
                messages.success(request, "Password reset link sent! Please check your email.")
            else:
                messages.error(request, "No user found with that email.")
    else:
        form = PasswordResetForm()
    return render(request, 'mytemplates/forgotpassword.html', {'form': form})


def custom_reset_password_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = DjangoUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, DjangoUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'mytemplates/password_reset_form.html', {'form': form})
    else:
        messages.error(request, 'The reset link is invalid or has expired.')
        return redirect('forgotpassword')



def bidding(request):
    return render(request, 'mytemplates/bidding.html')

from django.db.models import Q

def product(request):
    query = request.GET.get('q')
    admin_products = Product.objects.filter(user__is_superuser=True)

    if query:
        admin_products = admin_products.filter(
            Q(product_name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query)
        )

    return render(request, 'mytemplates/product.html', {'products': admin_products})



# ---------- AUTH ----------
def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('admin_dashboard' if user.is_staff else 'home')
        messages.error(request, "Invalid username or password.")
    return render(request, 'mytemplates/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect('login')
        messages.error(request, "Please fix the errors below.")
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'mytemplates/register.html', {'form': form})


# ---------- ADMIN ----------
def is_admin(user):
    return user.is_superuser or user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    user_counts = {
        'admin': User.objects.filter(is_staff=True).count(),
        'customer': User.objects.filter(is_staff=False).count()
    }
    order_status_counts = Order.objects.values('status').annotate(count=Count('status'))
    category_counts = Product.objects.values('category').annotate(count=Count('category'))

    context = {
        'total_users': User.objects.count(),
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'user_counts': user_counts,
        'order_status_counts': order_status_counts,
        'category_counts': category_counts
    }
    return render(request, 'mytemplates/admin_dashboard.html', context)

@user_passes_test(is_admin)
def admin_users(request):
    users = User.objects.all()
    return render(request, 'mytemplates/admin_users.html', {'users': users})

@user_passes_test(is_admin)
def admin_products(request):
    products = Product.objects.filter(user__is_staff=True)
    return render(request, 'mytemplates/admin_products.html', {'products': products})

@user_passes_test(is_admin)
def admin_all_orders(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'mytemplates/admin_orders.html', {'orders': orders})

@user_passes_test(is_admin)
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    new_status = request.POST.get("status")

    if new_status in ['pending', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        order.save()
        messages.success(request, "Order status updated successfully.")
    else:
        messages.error(request, "Invalid status selected.")

    return redirect('admin_all_orders')

@user_passes_test(is_admin)
def create_product(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        product = form.save(commit=False)
        product.user = request.user
        product.save()
        return redirect('admin_products')
    return render(request, 'mytemplates/create_product.html', {'form': form})

@user_passes_test(is_admin)
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('admin_products')
    return render(request, 'mytemplates/update_product.html', {'form': form})

@user_passes_test(is_admin)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_products')
    return render(request, 'mytemplates/delete_product.html', {'product': product})


# ---------- CART ----------
@login_required
def cart_view(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'mytemplates/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@require_POST
@login_required
def update_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        quantity = request.POST.get(f'quantity_{item.id}')
        size = request.POST.get(f'size_{item.id}')
        if quantity and int(quantity) > 0 and size:
            item.quantity = int(quantity)
            item.product.size = size
            item.product.save()
            item.save()
        else:
            messages.error(request, f"Invalid input for {item.product.product_name}.")
            return redirect('cart')
    messages.success(request, "Cart updated successfully.")
    return redirect('cart')

@require_POST
@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('cart')


# ---------- WISHLIST ----------
@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'mytemplates/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    exists = WishlistItem.objects.filter(user=request.user, product=product).exists()
    if exists:
        messages.warning(request, f"{product.product_name} is already in your wishlist.")
    else:
        WishlistItem.objects.create(user=request.user, product=product)
        messages.success(request, f"{product.product_name} added to your wishlist!")
    return redirect('product')

@login_required
def remove_wishlist_item(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, user=request.user)
    item.delete()
    return redirect('wishlist')


# ---------- ORDER ----------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Order

@login_required
def buy_now_checkout(request):
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity'))
            size = request.POST.get('size')
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            payment_method = request.POST.get('payment_method')

            product = get_object_or_404(Product, id=product_id)

            if quantity < 1:
                messages.error(request, "Quantity must be at least 1.")
                return redirect('product')

            total_price = product.price * quantity

            Order.objects.create(
                user=request.user,              # ✅ FK to authenticated user
                product=product,
                quantity=quantity,
                total_price=total_price,
                status='pending',
            )

            messages.success(request, "Order placed successfully!")
            return redirect('user_orders')

        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('product')

    return redirect('product')



@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'mytemplates/orders.html', {'orders': orders})



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.product_name} added to cart successfully!")
    return redirect('product')

@login_required
def checkout(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('cart')

        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                total_price=item.product.price * item.quantity,
                status='pending'
            )

        cart_items.delete()
        messages.success(request, "Your order has been placed successfully!")
        return redirect('user_orders')

    return redirect('cart')


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status.lower() == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, "Order has been cancelled.")
    else:
        messages.warning(request, "Only pending orders can be cancelled.")
    return redirect('user_orders')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage

def contact_us_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            full_name=full_name,
            email=email,
            message=message
        )
        messages.success(request, "Your message has been sent!")
        return redirect('contact')  # or wherever your contact page URL name is

    return render(request, 'contact.html')



from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ContactMessage

@login_required
def admin_messages_view(request):
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    paginator = Paginator(messages_list, 10)  # Show 5 messages per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'mytemplates/admin_messages.html', {'page_obj': page_obj})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Chat

@login_required
def chat_page(request):
    chats = Chat.objects.order_by('-timestamp')[:50]  # Last 50 messages (optional limit)
    return render(request, 'mytemplates/chat_page.html', {'chats': chats})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import CustomUserForm

User = get_user_model()

# -------------------- LIST USERS --------------------
def user_list_view(request):
    if not request.user.is_superuser:
        return redirect('home')  # Or show permission denied
    users = User.objects.all()
    return render(request, 'mytemplates/admin_users.html', {'users': users})

# -------------------- CREATE USER --------------------
from django.contrib import messages

def user_create_view(request):
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()  # Already sets password in the form
            messages.success(request, "User created successfully.")
            return redirect('admin_users')
        else:
            print(form.errors)  # For debugging
    else:
        form = CustomUserForm()

    return render(request, 'mytemplates/user_form.html', {'form': form})



# -------------------- EDIT USER --------------------
def user_edit_view(request, pk):
    if not request.user.is_superuser:
        return redirect('home')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "User updated successfully.")
            return redirect('admin_users')
    else:
        form = CustomUserForm(instance=user)
    return render(request, 'mytemplates/user_form.html', {'form': form})

# -------------------- DELETE USER --------------------
def delete_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('admin_users')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def profile_view(request):
    return render(request, 'mytemplates/profile.html', {'user': request.user})


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import CustomUserUpdateForm

User = get_user_model()

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = CustomUserUpdateForm(instance=request.user)
    return render(request, 'mytemplates/edit_profile.html', {'form': form})
