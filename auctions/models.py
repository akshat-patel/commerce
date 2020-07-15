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

class Comment(models.Model):
    comment = models.CharField(max_length=500, default="")
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE, related_name="comments", default=None)

    def __str__(self):
        return f"{self.user}: {self.comment}"

class Auction(models.Model):
    name = models.CharField(max_length=64,default="")
    price = models.PositiveIntegerField(validators=[MinValueValidator(0),])
    description = models.CharField(max_length=200, blank=True, default="")
    dateTime = models.DateTimeField(auto_now=True)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE, related_name="auctions", default=price)
    comment = models.ForeignKey(Comment, on_delete=models.DO_NOTHING, default=None)

    def __str__(self):
        return f"{self.name}: ${self.price}, {self.description}, {self.dateTime}, ${self.bid}"
