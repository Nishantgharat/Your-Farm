import os
from io import BytesIO
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.base import ModelState
from django.db.models.deletion import CASCADE
from django.db.models.fields import TextField
from django.db.models.fields.related import ForeignKey
# Create your models here.
from django.core.files.base import ContentFile
from datetime import timedelta
import datetime
from django.utils.timesince import timesince

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer', 'customer'),
        ('farmer', 'farmer'),
        ('admin', 'admin'),
    )
    user_type = models.CharField(
        max_length=200, null=True, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.user_type == 'admin'

    @property
    def is_customer(self):
        return self.user_type == 'customer'

    @property
    def is_farmer(self):
        return self.user_type == 'farmer'

    @property
    def has_aboutme(self):
        if self.is_farmer:
            return Aboutme.objects.filter(
        farmer=self).first()
    
    @property
    def has_donateme(self):
        if self.is_farmer:
            return Donateme.objects.filter(
        farmer=self, is_active=True).first()
    


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    sell_price = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    buy_price = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    sale_price = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    description = models.TextField(null=True)
    category = models.CharField(max_length=20, blank=True)
    in_stock = models.BooleanField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    @property
    def discount(self):
        if self.sale_price:
            return self.sell_price - self.sale_price

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "sell_price": self.sell_price,
            "buy_price": self.buy_price,
            "sale_price": self.sale_price,
            "description": self.description,
            "category": self.category,
            "in_stock": self.in_stock,
            "image": self.imageURL,
            "discount": self.discount,
        }


class Wishlist(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f"{self.customer} added {self.product} to wishlist"


class Comment(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True)
    description = models.TextField(max_length=250)
    created_on = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on', ]

    def __str__(self):
        return f"{self.customer} commented {self.title} on {self.product}"


class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Processing Initiated', 'Processing Initiated'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
    )
    customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS)
    complete = models.BooleanField(default=False)
    ordered_on = models.DateTimeField(default=None, null=True, blank=True)
    # date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.customer} order is {self.status}"

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.cust_get_total for item in orderitems])
        return total

    @property
    def get_cart_discount(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_discount for item in orderitems])
        return total

    @property
    def get_items_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_sell_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def get_status_class(self):
        status_class = {
            'Pending': 'danger',
            'Processing Initiated': 'danger',
            'In Transit': 'warning',
            'Delivered': 'success'}

        if self.status:
            return status_class[self.status]


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} {self.product} ordered by {self.order}"

    @property
    def cust_get_total(self):
        total = self.product.sell_price * self.quantity
        if self.product.sale_price:
            total = self.product.sale_price * self.quantity
        return total

    @property
    def get_sell_total(self):
        total = self.product.sell_price * self.quantity
        return total

    @property
    def get_discount(self):
        if self.product.sale_price:
            sale_total = self.product.sale_price * self.quantity
            total = self.product.sell_price * self.quantity
            return total - sale_total
        return 0


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL,  null=True)
    first_name = models.CharField(max_length=50,  null=True)
    last_name = models.CharField(max_length=50,  null=True)
    email = models.EmailField(max_length=254, null=True)
    phone_no = models.CharField(max_length=15, null=True)
    zipcode = models.CharField(max_length=10, null=True)
    country = models.CharField(max_length=30,  null=True)
    address_line1 = models.CharField(max_length=200,  null=True)
    address_line2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=30,  null=True)
    state = models.CharField(max_length=30,  null=True)

    def __str__(self):
        return f"Address of {self.user}"


class ShippingAddress(Address):
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, blank=True, null=True)


class Supplies(models.Model):
    STATUS = (
        ('Processing Initiated', 'Processing Initiated'),
        ('Checking Quality', 'Checking Quality'),
        ('Supplies Accepted', 'Supplies Accepted'),
    )
    farmer = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS)
    complete = models.BooleanField(default=False)
    supplied_on = models.DateTimeField(default=None, null=True, blank=True)
    # date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.farmer} {self.status}"

    @property
    def get_cart_total(self):
        supplyitems = self.supplyitem_set.all()
        total = sum([item.farm_get_total for item in supplyitems])
        return total

    @property
    def get_cart_items(self):
        supplyitems = self.supplyitem_set.all()
        total = sum([item.quantity for item in supplyitems])
        return total

    @property
    def get_status_class(self):
        status_class = {
            'Pending': 'danger',
            'Processing Initiated': 'danger',
            'Checking Quality': 'warning',
            'Supplies Accepted': 'success'}

        if self.status:
            return status_class[self.status]


class SupplyItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, blank=True, null=True)
    supply = models.ForeignKey(
        Supplies, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} {self.product} suplied by {self.supply}"

    @property
    def farm_get_total(self):
        total = self.product.buy_price * self.quantity
        return total


class Aboutme(models.Model):
    farmer = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    img = models.ImageField(null=True, blank=True)
    monthly_inc = models.DecimalField(
        max_digits=12, decimal_places=2, null=True)
    monthly_exp = models.DecimalField(
        max_digits=12, decimal_places=2, null=True)
    debt = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    descp = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.farmer.first_name}"

    @property
    def imageURL(self):
        try:
            url = self.img.url
        except:
            url = ''
        return url

    @property
    def monthly_savings(self):
        return self.monthly_inc - self.monthly_exp


class Donateme(models.Model):
    farmer = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    title = models.CharField(max_length=80, blank=True)
    descp = models.TextField(null=True, blank=True)
    img = models.ImageField(null=True, blank=True)
    fund_req = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    created_on = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.farmer.first_name}"

    @property
    def imageURL(self):
        try:
            url = self.img.url
        except:
            url = ''
        return url

    @property
    def fund_rasied(self):
        donations = self.donations_set.all()
        total = sum([donation.amount for donation in donations])
        if total:
            return total
    @property
    def fund_percent(self):
        if self.fund_rasied:
            percent = self.fund_rasied/self.fund_req * 100
            return percent

    @property
    def donors(self):
        total = self.donations_set.all()
        return len(total)
    
    @property
    def donate_time(self):
        now = datetime.datetime.now().date()
        diff = now - self.created_on
        if diff < timedelta(days=1):
            return "recently" # or w/e you wanted with the hours

        # remove trailing information from timesince    
        return timesince(self.created_on).split(", ")[0]+" ago"


class Donations(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    donateme = models.ForeignKey(
        Donateme, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    donated_on = models.DateField(auto_now_add=True)
