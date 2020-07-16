from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.core.validators import MinValueValidator

class User(AbstractUser):
    pass

class Bid(models.Model):
    bidValue = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0),])

    def __str__(self):
        return f"{self.bidValue} bid"

class Auction(models.Model):
    name = models.CharField(max_length=64,default="")
    bid = models.PositiveIntegerField(validators=[MinValueValidator(0),])
    description = models.CharField(max_length=200, blank=True, default="")
    dateTime = models.DateTimeField(auto_now=True)
    url = models.URLField(max_length=300, default="", blank=True)
    category=models.CharField(max_length=50, default="")

    def __str__(self):
        return f"{self.name}"

class Comment(models.Model):
    comment = models.CharField(max_length=500, default="")
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE, related_name="comments", default=None)
    listing = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="comments", blank=True, null=True)

    def __str__(self):
        return f"{self.user} on {self.listing}: {self.comment}"
