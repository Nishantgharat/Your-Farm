from .models import *
from django.contrib import messages

from urllib.parse import urlparse
import requests
from typing import DefaultDict
from PIL import Image
from datetime import datetime


def resize(image_pil, width=700, height=700):
    '''
    Resize PIL image keeping ratio and using white background.
    '''
    ratio_w = width / image_pil.width
    ratio_h = height / image_pil.height
    if ratio_w < ratio_h:
        # It must be fixed by width
        resize_width = width
        resize_height = round(ratio_w * image_pil.height)
    else:
        # Fixed by height
        resize_width = round(ratio_h * image_pil.width)
        resize_height = height
    image_resize = image_pil.resize(
        (resize_width, resize_height), Image.ANTIALIAS)
    image_resize = image_resize.convert("RGBA")
    background = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    offset = (round((width - resize_width) / 2),
              round((height - resize_height) / 2))
    background.paste(image_resize, offset, image_resize)
    return background.convert('RGB')


def cartData(request):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        request.session['cartStrings'] = dict()
        if request.user.user_type == "farmer":
            supply, created = Supplies.objects.get_or_create(
                farmer=request.user, complete=False)
            items = supply.supplyitem_set.all()
            cartItems = supply.get_cart_items
            request.session['cartStrings'] = {'cart': 'Supply', 'checkout': ''}
            request.session['cartItems'] = cartItems
            return{'order': supply, 'items': items, 'order_total': supply.get_cart_total, 'usertype': 'farmer'}

        order, created = Order.objects.get_or_create(
            customer=request.user, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
        request.session['cartStrings'] = {'cart': 'Shopping', }
        request.session['cartItems'] = cartItems

        return{'order': order, 'items': items, 'order_total': order.get_cart_total, 'usertype': request.user.user_type}


def get_image(files=None, img_url='', width=700, height=700):
    if files:
        img = files["img"]
        src = Image.open(img)
        return get_resized_img(src, width, height)

    else:
        name = urlparse(img_url).path.split('/')[-1]
        response = requests.get(img_url)
        if response.status_code == 200:
            src = Image.open(BytesIO(response.content))
            src = get_resized_img(src, width, height)
            return name, src


def get_resized_img(src, width, height):
    image = resize(src, width, height)
    thumb_io = BytesIO()
    image.save(thumb_io, format='PNG')
    return thumb_io.getvalue()


def createOrder(request):
    order = Order.objects.get(customer=request.user, complete=False)
    order.status = "Pending"
    order.complete = True
    order.ordered_on = datetime.now().strftime("%Y-%m-%d %H:%M")
    order.save()
    messages.error(request, "Order Placed Successfully",
                   extra_tags='success')
    return order


def createSupply(request):
    supply = Supplies.objects.get(farmer=request.user, complete=False)
    supply.status = "Processing Initiated"
    supply.complete = True
    supply.supplied_on = datetime.now().strftime("%Y-%m-%d %H:%M")
    supply.save()
    messages.error(request, "Supply Placed Successfully",
                   extra_tags='success')


def handleItem(request, product, action):
    if request.user.user_type == "farmer":
        supply, created = Supplies.objects.get_or_create(
            farmer=request.user, complete=False)
        supplyItem, created = SupplyItem.objects.get_or_create(
            supply=supply, product=product)
        actionItem(request, action, supplyItem)
    else:
        order, created = Order.objects.get_or_create(
            customer=request.user, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(
            order=order, product=product)
        actionItem(request, action, orderItem)


def actionItem(request, action, Item):
    if action == 'add':
        Item.quantity = (Item.quantity + 1)
        messages.error(request, 'Product added to cart', extra_tags='success')
    elif action == 'remove':
        Item.quantity = (Item.quantity - 1)
    elif action == 'delete':
        Item.delete()
        messages.error(request, 'Product removed from cart',
                       extra_tags='danger')
        return

    Item.save()

    if Item.quantity <= 0:
        Item.delete()
        messages.error(request, 'Product removed from cart',
                       extra_tags='danger')


def handleWishlist(request, product, action):
    wishlist, created = Wishlist.objects.get_or_create(
        customer=request.user, product=product)
    if action == 'add':
        wishlist.save()
    else:
        wishlist.delete()


def wishlistData(request, getProducts=False):
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(
            customer=request.user)
        request.session['wishlistCount'] = wishlist.count()
        if getProducts:
            return [wishlist.product.id for wishlist in wishlist]
        return wishlist


def productComments(product, getCommentlist=False):
    comments = Comment.objects.filter(product=product)
    if getCommentlist:
        return [comment.customer for comment in comments]
    return comments
