from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Bid, Auction, Comment
from .forms import AuctionForm

def index(request):
    auctions = Auction.objects.all()

    context = {
        'auctions': auctions,
        'username': request.user.username
    }
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
        #print(request.POST)
        form = AuctionForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.createdBy = User.objects.filter(username=request.user.username).get()
            listing.save()
            return redirect('index')
    context = {"form": listing}
    return render(request, "auctions/create.html", context)

def update(request, pk):
    form = AuctionForm()
    context = {"form": form}
    return render(request, "auctions/create.html", context)