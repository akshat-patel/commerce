from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import CreateView
from django.forms.models import model_to_dict
from django.db.models import Max
from datetime import datetime

from .models import User, Bid, Auction, Comment
from .forms import AuctionForm, BidForm, CommentForm

def index(request):
    auctions = Auction.objects.all()

    listings_maxValues = []
    for listing in auctions:
        listings_maxValues += [Bid.objects.filter(listing=listing.name).aggregate(Max('bidValue'))['bidValue__max']]

    highestBidBy = []
    for count, listing in enumerate(auctions):
        highestBidBy += [Bid.objects.filter(listing=listing.name).filter(bidValue=listings_maxValues[count]).get().user.username]

    context = {
        'auctions': enumerate(auctions),
        'username': request.user.username,
        'maxValues': listings_maxValues,
        'highestBidBy': highestBidBy
    }

    if request.method == "POST":
        if request.POST['Close']:
            for listing in auctions:
                if listing.id == int(request.POST['Close']):
                    listing.closed = True
                    listing.save()
    return render(request, "auctions/index.html", context)

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

def create(request):
    listing = AuctionForm()
    if request.method == "POST":
        form = AuctionForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.createdBy = User.objects.filter(username=request.user.username).get()
            listing.currentBid = Bid(bidValue=int(request.POST["bid"]), user=User.objects.filter(username=request.user.username).get(), listing=request.POST["name"])
            listing.currentBid.save()
            listing.save()
            return redirect('index')
    context = {"form": listing}
    return render(request, "auctions/create.html", context)

def update(request, pk):
    listing = Auction.objects.get(id=pk)
    original_name = listing.name
    form = AuctionForm(instance=listing)
    if request.method == "POST":
        form = AuctionForm(request.POST, instance=listing)
        if form.is_valid():
            listing = form.save(commit=False)
            if form.has_changed() and form.changed_data == ['bid']:
                listing.currentBid.delete()
            if form.has_changed() and form.changed_data == ['name']:
                breakpoint()
                bids = Bid.objects.filter(listing=original_name)
                for bid in bids:
                    bid.listing = request.POST["name"]
                    bid.save()
            listing.createdBy = request.user
            listing.save()
            return redirect('index')
    context = {"form": form, "updateTitle": 'Update'}
    return render(request, "auctions/create.html", context)

def delete(request, pk):
    auction = Auction.objects.get(id=pk)
    if request.method == "POST":
        Bid.objects.filter(listing=auction.name).delete()
        auction.delete()
        request.session.modified = True
        return redirect('index')

    if request.method == "GET":
        return render(request, "auctions/delete.html", {
            'auction': auction,
            'route': 'listing'
        })

    context= {
        'auction': auction,
        'route': 'index'
    }

    return render(request, "auctions/delete.html", context)

def listing(request, pk):
    auction = Auction.objects.get(id=pk)
    highest = Bid.objects.filter(listing=auction.name).aggregate(Max('bidValue'))['bidValue__max']
    bid = BidForm(instance=Bid.objects.filter(bidValue=highest)[0])
    comment = CommentForm()
    if request.method == "POST":
        commentForm = CommentForm(request.POST)
        bidForm = BidForm(request.POST, instance=Bid.objects.filter(bidValue=highest)[0])
        if 'bidValue' in request.POST:
            if int(request.POST['bidValue']) <= highest:
                return render(request, 'auctions/display.html', {
                    'error': 'Your bid has to be greater than the current bid.',
                    'listing': auction,
                    'username': request.user.username,
                    'highest': highest,
                    'bidForm': bid,
                    'highestBidBy': Bid.objects.filter(listing=auction.name).filter(bidValue=highest).get().user.username
                })
            if bidForm.is_valid():
                if Bid.objects.filter(listing=auction.name).filter(user=request.user).count() == 1:
                    Bid.objects.filter(listing=auction.name).filter(user=request.user).get().delete()
                bid = bidForm.save(commit=False)
                bid = Bid(bidValue=bid.bidValue, user=request.user, listing=auction.name)
                bid.save()
        
        if 'comment' in request.POST:
            if commentForm.is_valid():
                comment = commentForm.save(commit=False)
                comment = Comment(comment=comment.comment, user=request.user, listing=auction.name)
                comment.save()

        if 'Watchlist' in request.POST:
            if 'watchlist' not in request.session:
                request.session['watchlist'] = []
            if auction.name not in request.session['watchlist']:
                request.session['watchlist'] += [auction.name]
            request.session.modified = True
            auction.watchlisted = True
            auction.save()

        return redirect('listing', pk)
    
    comments = Comment.objects.all()

    return render(request, "auctions/display.html", {
        'listing': auction, 'username': request.user.username, 'highest': highest, 'bidForm': bid, 'highestBidBy': Bid.objects.filter(listing=auction.name).filter(bidValue=highest).get().user.username, 'commentForm': comment, 'comments': comments
    })

def watchlist(request, username):
    auctions = []
    
    for listing in request.session['watchlist']:
        if listing in [auction.name for auction in Auction.objects.all()]:
            auctions += [Auction.objects.filter(name=listing).get()]

    listings_maxValues = []
    for listing in auctions:
        listings_maxValues += [Bid.objects.filter(listing=listing.name).aggregate(Max('bidValue'))['bidValue__max']]

    highestBidBy = []
    for count, listing in enumerate(auctions):
        highestBidBy += [Bid.objects.filter(listing=listing.name).filter(bidValue=listings_maxValues[count]).get().user.username]
    
    if request.method == "POST":
        auction = Auction.objects.get(pk=int(request.POST["Remove"]))
        request.session['watchlist'].remove(auction.name)
        auction.watchlisted = False
        auction.save()
        index = auctions.index(auction)
        del auctions[index]
        del listings_maxValues[index]
        del highestBidBy[index]


    return render(request, 'auctions/watchlist.html', {
        'auctions': enumerate(auctions),
        'username': request.user.username,
        'maxValues': listings_maxValues,
        'highestBidBy': highestBidBy
    })

def categories(request, *args ,**kwargs):
    if kwargs:
        auctions = Auction.objects.filter(category=kwargs['category']).filter(closed=False)

        listings_maxValues = []
        for listing in auctions:
            listings_maxValues += [Bid.objects.filter(listing=listing.name).aggregate(Max('bidValue'))['bidValue__max']]

        highestBidBy = []
        for count, listing in enumerate(auctions):
            highestBidBy += [Bid.objects.filter(listing=listing.name).filter(bidValue=listings_maxValues[count]).get().user.username]

        context = {
            'auctions': enumerate(auctions),
            'username': request.user.username,
            'maxValues': listings_maxValues,
            'highestBidBy': highestBidBy,
            'category': kwargs['category']
        }

        return render(request, 'auctions/index.html', context)

    categories = {}
    choices = Auction.CATEGORY_CHOICES
    auctions = Auction.objects.all()
    for choice in choices:
        for listing in auctions:
            if listing.category == choice[0]:
                if listing.category not in categories:
                    categories[listing.category] = []    
                categories[listing.category] += [listing]

    
    return render(request, 'auctions/categories.html', {
        'categories': choices
    })