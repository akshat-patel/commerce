from django import forms
from .models import Auction, Bid, Comment


class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ["name", "bid", "category", "description", 'url']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["bidValue"]       

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['comment'].widget.attrs.update({'class': 'form-control col-sm-24'}, style='max-height: 7em')