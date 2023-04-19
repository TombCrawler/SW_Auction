from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, ValidationError
from datetime import timezone
from datetime import datetime
from datetime import timedelta
from typing import Optional


class User(AbstractUser):
    watched_auctions = models.ManyToManyField(
        "Auction", blank=True, related_name="watchers"
    )


class Category(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, unique=True)

    @property
    def active_auctions(self):
        return self.auctions.filter(end_date__gt=datetime.now(timezone.utc)) #this "auctions" comes from the related_name of the category in the Auction class

    @property
    def len_active_auctions(self):
        return len(self.active_auctions)

    def __str__(self):
        return f"<Category id={self.id},name={self.name}>"


class Auction(models.Model):
    DAYS = 7
    title = models.CharField(max_length=64, blank=False, null=False)
    description = models.CharField(max_length=512)
    starting_bid = models.FloatField(validators=[MinValueValidator(0.001)])
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="auctions",
    )
    create_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=False, null=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False, null=False, related_name="auctions"
    )
    _winner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="won_auctions",
        blank=True,
        null=True,
    )

    def full_clean(self, *args, **kwargs):
        # The parent class for the super() is models.Model.
        super().full_clean(*args, **kwargs)

        if self.end_date and self.end_date < datetime.now(timezone.utc):
            raise ValidationError("End date must be after create date")

    def save(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = datetime.now(timezone.utc) + timedelta(days=self.DAYS)
        super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool: #-> is used to indicate the return type
        end_str = str(self.end_date).split(".")[0]
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        return end_str > now_str

    @property
    def winner(self) -> Optional[User]: # The Optional type hint is from typing module used to indicate that the method can return either an object of type User or None.
        if self.is_active:
            return None
        if self._winner is None:
            user = self.bids.order_by("-amount").first()
            if user:
                self._winner = user.user
                self.save()
        return self._winner

    @property
    def highest_bid(self) -> Optional[float]:
        if self.bids.count() == 0:
            return None
        return self.bids.order_by("-amount").first().amount

    def close(self):
        self.end_date = datetime.now(timezone.utc)
        print(f"Closing auction {self.id}")
        self.save()

    def __str__(self):
        create_str = str(self.create_date).split(".")[0]
        end_str = str(self.end_date).split(".")[0]
        return (
            f"<Auction: id={self.id}, title={self.title},"
            f" description={self.description}, starting_bid={self.starting_bid},"
            f" highest_bid={self.highest_bid},"
            f" image_url={self.image_url}, category={self.category},"
            f" create_date={create_str}, end_date={end_str},"
            f" user={self.user}, winner={self.winner}>"
        )


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="bids")
    amount = models.FloatField(validators=[MinValueValidator(0.001)])

    def clean(self):
        if self.amount <= self.auction.starting_bid:
            raise ValidationError("Bid amount must be greater than starting bid")

        if not self.auction.is_active:
            raise ValidationError("Auction is no longer active")

        if self.user == self.auction.user:
            raise ValidationError("Cannot bid on own auction")

        if self.auction.winner:
            raise ValidationError("Cannot bid on auction with winner")

        if self.auction.highest_bid and self.amount <= self.auction.highest_bid:
            raise ValidationError("Bid amount must be greater than highest bid")

    def __str__(self):
        return (
            f"<Bid: id={self.id}, user={self.user}, auction={self.auction},"
            f" amount={self.amount}>"
        )


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auction = models.ForeignKey(
        Auction, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.CharField(max_length=512, blank=False, null=False)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"<Comment: id={self.id}, user={self.user}, auction={self.auction},"
            f" text={self.text}>"
        )