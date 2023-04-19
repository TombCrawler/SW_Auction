from django import forms
from .models import *

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'bid', 'image_url', 'category']
        exclude= ['current_bid', 'end_time', 'final_bid', 'closed', 'date_created', ]


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['price', 'id']
    


    def clean_price(self): 
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError('Bid price must be greater than zero.')
        return price
    
    def bid_id(self):
        bid_id = self.cleaned_data['id']
        return bid_id
    

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']