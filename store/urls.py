from django.urls import path
from .import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register/<str:usertype>", views.register, name="register"),

    path("shop", views.shop, name="shop"),
    path("detail/<str:id>", views.detail, name="detail"),
    path("cart", views.cart, name="cart"),
    path("wishlist", views.wishlist, name="wishlist"),
    
    path("checkout", views.checkout, name="checkout"),
    path("add_product", views.add_product, name="add_product"),
    path('orderhistory', views.orderhistory, name='orderhistory'),
    path('orderdetail/<str:id>', views.orderdetail, name='orderdetail'),
    path('supplyhistory', views.supplyhistory, name='supplyhistory'),
    path('supplydetail/<str:id>', views.supplydetail, name='supplydetail'),


    path('create_donateme', views.createDonateme, name='create_donateme'),
    path('donateme/<str:id>', views.donatemeDetail, name='donateme'),

    
    path('create_aboutme', views.createAboutme, name='create_aboutme'),
    path('aboutme/<str:id>', views.aboutmeDetail, name='aboutme'),
    
    
    path("proceedtopay", views.proceedToPay, name="proceedtopay"),
    path("success", views.orderSucess, name="success"),
    path("cancel", views.orderCancel, name="cancel"),

    # Api
    path('update_item', views.updateItem, name='update_item'),
    path('update_wishlist', views.updateWishlist, name='update_wishlist'),
    path('modal', views.modal, name='modal'),
    path("create-checkout-session", views.checkoutsession,
         name="create-checkout-session"),
    path("product_comment/<str:id>", views.addComment, name="product_comment"),
]
