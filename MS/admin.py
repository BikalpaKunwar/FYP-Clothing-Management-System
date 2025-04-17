from django.contrib import admin
from .models import *

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Bid)
admin.site.register(Order)
admin.site.register(Rating)
admin.site.register(Chat)
admin.site.register(Coupon)