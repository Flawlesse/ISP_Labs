from django.contrib import admin
from .models import UserAccount, Wallet

# Register your models here.
admin.site.register(UserAccount)
admin.site.register(Wallet)
