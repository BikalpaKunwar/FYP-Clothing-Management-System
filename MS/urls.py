from django.urls import path
from . import views

urlpatterns = [
# --- AUTH ---
path('', views.home, name='home'),
path('login/', views.login_view, name='login'),
path('logout/', views.logout_view, name='logout'),
path('register/', views.register, name='register'),
path('forgotpassword/', views.forgotpassword, name='forgotpassword'),

# --- PUBLIC PAGES ---
path('product/', views.product, name='product'),
path('bidding/', views.bidding, name='bidding'),
path('aboutus/', views.aboutus, name='aboutus'),
path('contact/', views.contact, name='contact'),
path('chat/', views.chat_page, name='chat_page'),


# --- CART ---
path('cart/', views.cart_view, name='cart'),
path('cart/update/', views.update_cart, name='update_cart'),
path('cart/checkout/', views.checkout, name='checkout'),
path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
path('cart/remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),

# --- WISHLIST ---
path('wishlist/', views.wishlist_view, name='wishlist'),
path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
path('remove-wishlist/<int:item_id>/', views.remove_wishlist_item, name='remove_wishlist_item'),

# --- BUY NOW / ORDERS ---
path('buy-now-checkout/', views.buy_now_checkout, name='buy_now_checkout'),
path('orders/', views.user_orders, name='user_orders'),
path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
path('profile/', views.profile_view, name='profile'),
path('profile/edit/', views.edit_profile_view, name='edit_profile'),


    # --- ADMIN DASHBOARD ---
path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('dashboard/users/', views.admin_users, name='admin_users'),
path('dashboard/orders/', views.admin_all_orders, name='admin_all_orders'),
path('dashboard/orders/update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
path('dashboard/messages/', views.admin_messages_view, name='admin_messages'),

    # --- ADMIN PRODUCTS ---
path('dashboard/products/', views.admin_products, name='admin_products'),
path('dashboard/products/create/', views.create_product, name='create_product'),
path('dashboard/products/update/<int:pk>/', views.update_product, name='update_product'),
path('dashboard/products/delete/<int:pk>/', views.delete_product, name='delete_product'),


path('dashboard/users/', views.user_list_view, name='admin_users'),
path('dashboard/users/create/', views.user_create_view, name='create_user'),
path('dashboard/users/edit/<int:pk>/', views.user_edit_view, name='edit_user'),
path('dashboard/users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]
