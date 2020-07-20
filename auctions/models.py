from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.core.validators import MinValueValidator

class User(AbstractUser):
    pass

class Bid(models.Model):
    bidValue = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0),])
    user=models.ForeignKey(User, blank=False, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"${self.bidValue} bid by {self.user}"

class Comment(models.Model):
    comment = models.CharField(max_length=500, default="")
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE, related_name="comments", default=None)

    def __str__(self):
        return f"{self.user}: {self.comment}"

class Auction(models.Model):

    CATEGORY_CHOICES = [
        ('Toys', 'Toys'),
        ('Home', 'Home'),
        ('Electronics', 'Electronics'),
        ('Fashion', 'Fashion'),
    ]
    name = models.CharField(max_length=64,default="")
    bid = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0),])
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='None')
    description = models.CharField(max_length=200, blank=True, default="")
    dateTime = models.DateTimeField(auto_now_add=True, name="datetime")
    url = models.URLField(max_length=300, default="", blank=True)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions", blank=True, null=True, default='')

    def __str__(self):
        return f"{self.name}"
