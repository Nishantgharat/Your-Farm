from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Product)
# admin.site.register(Order)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'status', 'complete', 'ordered_on']
    list_filter = ['ordered_on', 'status']
    ordering = ['ordered_on']
    


admin.site.register(OrderItem)
admin.site.register(Address)
admin.site.register(ShippingAddress)
# admin.site.register(Supplies)


@admin.register(Supplies)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'status', 'complete', 'supplied_on']
    list_filter = ['supplied_on', 'status']
    ordering = ['supplied_on']


admin.site.register(SupplyItem)
admin.site.register(Wishlist)
admin.site.register(Comment)
admin.site.register(Donateme)
admin.site.register(Donations)
admin.site.register(Aboutme)
