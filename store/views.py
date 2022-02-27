from store.decorators import allowed_users, unauthenticated_user
from django import http
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.deletion import SET_NULL
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import stripe
import json
from django.conf import settings
# Create your views here.

from .forms import AddProduct, AddressForm, DonatemeForm, AboutmeForm
from .models import *
from urllib.parse import urlparse
import requests
from django.core.files.base import ContentFile
from io import BytesIO

from .utils import *
from django.forms.models import model_to_dict
from django.http import JsonResponse
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url="login") # home
def index(request):
    products = Product.objects.filter(in_stock=True)[:4]
    context = {"products": products}
    if request.user.is_authenticated:
        cartData(request)
        wishlistData(request)
        # messages.error(request, request.user.has_aboutme, extra_tags='success')
    return render(request, "store/index.html", context)

@unauthenticated_user
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(
                request, 'Invalid username or password.', extra_tags='danger')
    return render(request, "store/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@unauthenticated_user
def register(request, usertype):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["email"]
        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            messages.error(request, 'Password do not match',
                           extra_tags='danger')
            return render(request, "store/register.html", {
                "usertype": usertype,
            })

        # Attempt to create new farmer user
        try:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=username,
                password=password,
                user_type=usertype.lower()
            )
            user.save()

        except IntegrityError:
            messages.error(
                request, 'User with email already exsists', extra_tags='danger')
            return render(request, "store/register.html", {
                "usertype": usertype,
            })
        login(request, user)

        return HttpResponseRedirect(reverse("index"))

    return render(request, "store/register.html", {
        "usertype": usertype,
    })

@login_required(login_url="login")
@allowed_users(allowed_rolls=["admin"])
def add_product(request):
    if request.method == "POST":
        form = AddProduct(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data["name"]
            sell_price = form.cleaned_data["sell_price"]
            buy_price = form.cleaned_data["buy_price"]
            sale_price = form.cleaned_data["sale_price"]
            if sale_price == "":
                sale_price = None
            description = form.cleaned_data["description"]
            category = form.cleaned_data["category"]
            in_stock = form.cleaned_data["in_stock"]
            upload_choice = form.cleaned_data["upload_choice"]
            product = Product(name=name, sell_price=sell_price, buy_price=buy_price,
                              sale_price=sale_price, description=description, category=category, in_stock=in_stock)

            if upload_choice == '2':
                files = request.FILES
                src = get_image(files=files)

            elif upload_choice == '1':
                img_url = form.cleaned_data["img_url"]
                name, src = get_image(img_url=img_url)

            if src:
                product.image.save(name, ContentFile(
                    src), save=True)

            product.save()

            messages.error(
                request, '✔️ Product Added Successfully', extra_tags='success')
            # messages.error(request, files, extra_tags='success')
        # else:
        #     form = CreateListing()

        else:
            print(form.errors)
    return render(request, "store/add_product.html", {
        "form": AddProduct()
    })

@login_required(login_url="login")
def shop(request):
    products = Product.objects.all()
    # messages.error(
    #     request, request.session['wishlistCount'], extra_tags='success')
    context = {"products": products,
               "wishlist": wishlistData(request, True)}
    return render(request, "store/shop.html", context)


@login_required(login_url="login")
def detail(request, id):
    product = Product.objects.get(pk=id)
    similar_products = Product.objects.exclude(
        pk=id).filter(category=product.category).filter(in_stock=True)[:4]
    supplies = list(SupplyItem.objects.filter(
        product=product).order_by('-supply__supplied_on').values_list('supply__farmer', flat=True))
    farmer_list=[]
    for id in supplies:
        if id not in farmer_list:
            farmer_list.append(id)
    print(farmer_list)
    farmers= User.objects.filter(pk__in=farmer_list)
    # messages.error(
    #     request, farmers, extra_tags='success')
    context = {"product": product,
               "similar_products": similar_products,
               "wishlist": wishlistData(request, True),
               "comments": productComments(product),
               "comment_list": productComments(product, True),
               "farmers": farmers, }
    return render(request, "store/detail.html", context)


@login_required(login_url="login")
def cart(request):
    context = cartData(request)
    return render(request, "store/cart.html", context)


@login_required(login_url="login")
def wishlist(request):
    context = {"wishlist": wishlistData(request)}
    return render(request, "store/wishlist.html", context)


@login_required(login_url="login")
def addComment(request, id):
    if request.method == "POST":
        product = Product.objects.get(pk=id)
        title = request.POST['title']
        description = request.POST['description']
        comment = Comment.objects.create(
            customer=request.user, product=product, title=title, description=description)
        comment.save()
        return redirect('detail', id=product.id)


@login_required(login_url="login")
def checkout(request):
    context = cartData(request)
    if request.method == 'POST':
        if Address.objects.filter(user=request.user).exists():
            if request.user.user_type == "farmer":
                createSupply(request)
                cartData(request)
                return redirect('supplyhistory')
            return render(request, 'store/pay.html', context)
        adrs_form = AddressForm(request.POST)
        if adrs_form.is_valid():
            adrs_form = adrs_form.save(commit=False)
            adrs_form.user = request.user
            adrs_form.save()
            if request.user.user_type == "farmer":
                createSupply(request)
                cartData(request)
                return redirect('supplyhistory')
            return render(request, 'store/pay.html', context)
        else:
            context["adrs_form"] = adrs_form
            return render(request, 'store/checkout.html', context)
    else:
        if Address.objects.filter(user=request.user).exists():
            address = Address.objects.get(user=request.user)
            adrs_form = AddressForm(initial=model_to_dict(address))
            messages.error(request, 'final else', extra_tags='success')
            context["adrs_form"] = adrs_form
            context["user_address"] = address
            return render(request, 'store/checkout.html', context)
    context["adrs_form"] = AddressForm(instance=request.user)
    return render(request, 'store/checkout.html',  context)


@login_required(login_url="login")
def updateItem(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']
        print(productId, action)
        product = Product.objects.get(id=productId)

        handleItem(request, product, action)
        cartData(request)
        return JsonResponse('Item was added', safe=False)


@login_required(login_url="login")
def updateWishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        productId = data['productId']
        action = data['action']
        product = Product.objects.get(id=productId)
        handleWishlist(request, product, action)
        return JsonResponse('Item was added', safe=False)


def modal(request):
    print("Inside modal")
    if request.method == 'POST':
        data = json.loads(request.body)
        productId = data['productId']
        product = Product.objects.get(id=productId)
        return JsonResponse(product.serialize(), safe=False)


@login_required(login_url="login")
def orderhistory(request):
    if Order.objects.filter(customer=request.user, complete=True).exists():
        orders = Order.objects.all().filter(customer=request.user,
                                            complete=True).order_by('-ordered_on')
        context = {"orders": orders}
        # messages.error(request, context, extra_tags='success')
        return render(request, 'store/order_history.html', context)
    return render(request, 'store/order_history.html')


@login_required(login_url="login")
def orderdetail(request, id):
    if Order.objects.filter(pk=id).exists():
        order = Order.objects.get(pk=id)
        items = order.orderitem_set.all()
        # changes needed in order model. Attach shipping address to each order.
        address = Address.objects.get(user=request.user)

        context = {"order": order, "items": items, "user_address": address}
        return render(request, 'store/order_detail.html', context)
    return render(request, 'store/order_detail.html')


@login_required(login_url="login")
def supplyhistory(request):
    if Supplies.objects.filter(farmer=request.user, complete=True).exists():
        supplies = Supplies.objects.all().filter(
            farmer=request.user, complete=True).order_by('-supplied_on')
        context = {"orders": supplies}
        # messages.error(request, context, extra_tags='success')
        return render(request, 'store/order_history.html', context)
    return render(request, 'store/order_history.html')


@login_required(login_url="login")
def supplydetail(request, id):
    if Supplies.objects.filter(pk=id).exists():
        supplies = Supplies.objects.get(pk=id)
        items = supplies.supplyitem_set.all()
        # changes needed in order model. Attach shipping address to each order.
        address = Address.objects.get(user=request.user)

        context = {"order": supplies, "items": items, "user_address": address}
        return render(request, 'store/order_detail.html', context)
    return render(request, 'store/order_detail.html')


# payment integration
@login_required(login_url="login")
def checkoutsession(request):

    stripe.api_key = settings.STRIPE_SECRET_KEY
    carttotal = cartData(request)
    unit_amount = int(carttotal.get('order_total'))*100
    YOUR_DOMAIN = "http://127.0.0.1:8000"
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'inr',
                    'unit_amount': unit_amount,
                    'product_data': {
                        'name': request.user.username.capitalize(),
                        'images': ['https://image.freepik.com/free-vector/credit-card-payment-concept-landing-page_52683-28270.jpg'],
                    },
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url=YOUR_DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=YOUR_DOMAIN + '/cancel',
    )

    return JsonResponse({
        'id': checkout_session.id
    })


@login_required(login_url="login")
def orderSucess(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session_id = request.GET.get('session_id')
    if session_id:
        session = stripe.checkout.Session.retrieve(session_id)
        order = createOrder(request)
        context = {'order': order}
        return render(request, 'store/success.html', context)
    return redirect('cart')


@login_required(login_url="login")
def orderCancel(request):
    return render(request, 'store/cancel.html')


@login_required(login_url="login")
def proceedToPay(request):
    if Address.objects.filter(user=request.user).exists():
        context = cartData(request)
    return render(request, 'store/pay.html', context)


@login_required(login_url="login")
def createAboutme(request):
    if request.user.has_aboutme:
        return redirect('aboutme',id=request.user.has_aboutme.id)
    if request.method == "POST":
        form = AboutmeForm(request.POST, request.FILES)
        if form.is_valid():
            monthly_inc = form.cleaned_data["monthly_inc"]
            monthly_exp = form.cleaned_data["monthly_exp"]
            debt = form.cleaned_data["debt"]
            descp = form.cleaned_data["descp"]
            if debt == "":
                debt = None
            upload_choice = form.cleaned_data["upload_choice"]
            aboutme = Aboutme(farmer=request.user,
                              monthly_inc=monthly_inc,
                              monthly_exp=monthly_exp,
                              debt=debt,
                              descp=descp,)

            if upload_choice == '2':
                files = request.FILES
                src = get_image(files=files, width=800)

            elif upload_choice == '1':
                img_url = form.cleaned_data["img_url"]
                name, src = get_image(img_url=img_url, width=800)

            if src:
                aboutme.img.save(name, ContentFile(
                    src), save=True)

            aboutme.save()
            messages.error(
                request, '✔️ About me page created', extra_tags='success')
        else:
            print(form.errors)
    return render(request, "store/create_aboutme.html", {
        "form": AboutmeForm()
    })


@login_required(login_url="login")
def aboutmeDetail(request, id):
    aboutme = get_object_or_404(Aboutme, pk=id)
    donateme = Donateme.objects.filter(
        farmer=aboutme.farmer, is_active=True).first()
    messages.error(
        request, donateme, extra_tags='success')
    context = {"aboutme": aboutme, "donateme": donateme}
    return render(request, "store/aboutme.html", context)


@login_required(login_url="login")
def createDonateme(request):
    if request.user.has_aboutme:
        if request.user.has_donateme:
            return redirect('donateme',id=request.user.has_donateme.id)
    else:
        return redirect('create_aboutme')
    if request.method == "POST":
        form = DonatemeForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            descp = form.cleaned_data["descp"]
            fund_req = form.cleaned_data["fund_req"]
            upload_choice = form.cleaned_data["upload_choice"]
            donateme = Donateme(farmer=request.user, title=title,
                                descp=descp,
                                fund_req=fund_req,)
            if upload_choice == '2':
                files = request.FILES
                src = get_image(files=files, width=800)

            elif upload_choice == '1':
                img_url = form.cleaned_data["img_url"]
                name, src = get_image(img_url=img_url, width=800)

            if src:
                donateme.img.save(name, ContentFile(
                    src), save=True)

            donateme.save()
            messages.error(
                request, '✔️ Donate me page created', extra_tags='success')
        else:
            print(form.errors)
    return render(request, "store/create_donateme.html", {
        "form": DonatemeForm()
    })


@login_required(login_url="login")
def donatemeDetail(request, id):
    donateme = get_object_or_404(Donateme, pk=id)
    messages.error(
        request, donateme.farmer, extra_tags='success')
    aboutme = Aboutme.objects.get(farmer=donateme.farmer)
    recent_donations = Donations.objects.filter(donateme=donateme).order_by('-donated_on')
    context = {"donateme": donateme, "aboutme": aboutme, "recent_donations":recent_donations}
    return render(request, "store/donateme.html", context)
