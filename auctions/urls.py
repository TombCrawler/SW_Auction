from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_watchlist/<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist/<int:listing_id>", views.remove_watchlist, name="remove_watchlist"),
    path("place_bid/<int:listing_id>", views.place_bid, name="place_bid"),
    path("close_bid/<int:listing_id>", views.close_bid, name="close_bid"),
    path("open_bid/<int:listing_id>", views.open_bid, name="open_bid"),
    path("post_comment/<int:listing_id>", views.post_comment, name="post_comment"),
    path("category", views.category, name="category"),
    path("category_detail/<str:category>", views.category_detail, name="category_detail")
]
