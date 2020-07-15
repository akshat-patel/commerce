from django.contrib import admin
from .models import User, Bid, Auction, Comment
from django.contrib.auth.admin import UserAdmin
# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Bid)
admin.site.register(Auction)
admin.site.register(Comment)
