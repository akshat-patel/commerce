from django import forms
from .models import Auction, Bid
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ["name", "bid", "category", "description", 'url']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["bidValue"]       