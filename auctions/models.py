from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models


class User(AbstractUser):
    pass
    def __str__(self):
        return f"{self.id}: {self.username}"



class Listing(models.Model):
    category_item = (
        ('weapon', 'Weapon'),
        ('ship', 'Ship'),
        ('vehicle', 'Vehicle'),
        ('droid', 'Droid')
    )
    title = models.CharField(max_length=50)
    description = models.TextField(max_length=250)
    bid = models.DecimalField(max_digits=8, decimal_places=2)
    current_bid = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    image_url = models.URLField()
    category = models.CharField(max_length=20, choices=category_item)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    final_bid = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.id}: {self.title}: Start {self.bid}/ category is {self.category.capitalize()}/ created by {self.user.username}. Closed? {self.closed}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bidding_item")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}-{self.user.username} - {self.listing.title} - {self.price} at {self.created_at}"
    


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'listing')


class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=250, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text} posted by {self.user.username} on {self.created_date}"