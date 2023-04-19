from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings" : listings
    })
    

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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            # save() method with commit=False parameter allows you to 
            # save a model instance to the database without committing the transaction immediately.
            listing = form.save(commit=False)
            listing.user=request.user
            
            # save() belongs to the "django.db.models.Model" class and the save() method stores/updates the info in database
            listing.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = ListingForm()
    
    return render(request, 'auctions/create_listing.html',{
        'form':form
    })


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    # this already returns an int of the bid field
    # bid = Listing.objects.values_list('bid', flat=True).get(pk=listing_id)
    # bid = listing.bid
    # bid = bid * 3
    # print(f"Hey!{bid}")
    return render(request, "auctions/listing.html",{
        "listing": listing
        # "bid" : bid
    })


def watchlist(request):
    watchlist = Watchlist.objects.filter(user=request.user)
    return render(request, "auctions/watchlist.html", {
        "watchlist" : watchlist
    })

@login_required
def add_watchlist(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        try:    
            Watchlist.objects.create(user=request.user, listing=listing)
            return HttpResponseRedirect(reverse('watchlist'))

        except:
             return HttpResponseRedirect(reverse('watchlist'))
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))
    

@login_required
def remove_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST":
        Watchlist.objects.filter(user=request.user, listing=listing).delete()
        return redirect('watchlist')
    else:
        return render(request, "auctions/remove.html",{
            "listing" : listing
        })
    

def place_bid(request, listing_id):
   listing = Listing.objects.get(id=listing_id)
   if request.method == "POST":
       form= BidForm(request.POST)
       if form.is_valid():
           bid = form.save(commit=False)
           bid.user = request.user
           bid.listing = listing
           bid.save()
           # Retuens the full Bid's objects of the specific bid ID, like " 110-vader - Dooku's Lightsaber - 4502.00"
           bid_obj = Bid.objects.filter(pk=bid.id)
           # check if it exists
           if not bid_obj:
               form = BidForm()
           # this means it exists
           bid_obj = bid_obj[0]
           # get the bid price the user just input as an int
           int_bid_price = bid_obj.price
           # listing.bid returns the current bid as an int so that you can use conditionals
           if int_bid_price <= listing.bid:
               form = BidForm()
               messages.error(request, 'You bid is lower than the current bid.')
               return HttpResponseRedirect(reverse("place_bid", args=[listing_id]))
           else:
            # get a query set of the specified price
            bid_price = Bid.objects.filter(id=bid.id).values('price')
            # update the current "bid" to= a new bid, "bid_price"
            Listing.objects.filter(id=listing_id).update(bid=bid_price)
            messages.success(request, 'Your bid was placed successfully!')
            return redirect('place_bid', listing_id=listing.id)
        # Invalid form
       else:
           form = BidForm()
           messages.error(request, '10 digits are max')
           return HttpResponseRedirect(reverse("place_bid", args=[listing_id]))
   
   
   else:  
          form = BidForm()
          comment_form = CommentForm()
          bid_obj = Bid.objects.filter(listing_id=listing_id)
          comments = Comment.objects.filter(listing_id=listing_id)
          if not bid_obj:
              messages.error(request, 'Place a first bid!')
              return render(request, "auctions/place_bid.html",{
                    "form": form,
                    "listing" : listing,
                    "comment_form" : comment_form,
                    "comments" : comments
              })
          else:
              bid_obj = Bid.objects.filter(listing_id=listing_id).order_by('-price')
              highest_bidder = bid_obj.first().user.username
              last_bid_date = bid_obj.first().created_at
              return render(request, "auctions/place_bid.html",{
                        "form": form,
                        "listing" : listing,
                        "highest_bidder" : highest_bidder,
                        "last_bid_date" : last_bid_date,
                        "comment_form" : comment_form,
                        "comments" : comments
                    })


@login_required
def close_bid(request, listing_id):
  if request.method == "POST":
    listing = get_object_or_404(Listing, id=listing_id)
    if request.user == listing.user:
       listing.closed = True
    #    highest_bid = Bid.objects.filter(listing=listing).order_by('-price').first()
    #    if highest_bid:
    #        listing.winning_bid = highest_bid.price
       listing.save()
       messages.success(request, 'You Successfully closed the bid!')
       return HttpResponseRedirect(reverse("place_bid", args=[listing_id]))
    else:
       pass
       messages.error(request, "Not a creator")
       return HttpResponseRedirect(reverse("place_bid", args=[listing_id]))
       
  else:
     return HttpResponseRedirect(reverse("place_bid", args=[listing_id]))
  

@login_required
def open_bid(request, listing_id):
    if request.method == "POST":
       listing = get_object_or_404(Listing, pk=listing_id)
       if request.user == listing.user:
           listing.closed = False
           listing.save() 


           return HttpResponseRedirect(reverse("place_bid", args=[listing_id]))
       else:
            pass
            messages.error(request, "Not a creator")
            return HttpResponseRedirect(reverse("place_bid", args=[listing_id]))
    else:
       return HttpResponseRedirect(reverse("place_bid", args=[listing_id]))
    

@login_required
def post_comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.listing = listing
            comment.user = request.user
            comment.save()
            return redirect("place_bid", listing_id=listing_id)
    else:
        form = CommentForm()
    return redirect("place_bid", listing_id=listing_id)


def category(request):
    categories = Listing.category.field.choices
    categories = [x[0] for x in categories]
    return render(request, "auctions/category.html", {
        "categories" : categories
    })

def category_detail(request, category):
          # the left category is the attribute of the Listing class, the right category is the category_detail function 
          # parameter which is comming in from the detail.html
          # And this line of code returns all the category related listings
          category_listings = Listing.objects.filter(category=category)
          return render(request, "auctions/category_detail.html", {
        "category_listings" : category_listings,
        "category" : category
    })
    #   elif category == "ship":
    #       ships = Listing.objects.filter(category="ship")
    #       return render(request, "auctions/category_detail.html", {
    #       "ships" : ships
    #   })
    #   elif category == "vehicle":
    #       vehicles = Listing.objects.filter(category="vehicle")
    #       return render(request, "auctions/category_detail.html", {
    #       "vehicles" : vehicles
    #   })
    #   elif category == "droid":
    #       droids = Listing.objects.filter(category="droid")
    #       print(f"Hey Droid!! {droids}")
    #       return render(request, "auctions/category_detail.html",{
    #            "droids" : droids              
    #       })
      









