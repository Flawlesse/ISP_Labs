from django.contrib import admin
from django.contrib.auth.models import User
from .models import Order, Account, Wallet
from .forms import AccountCreationForm
from django.contrib.auth.admin import UserAdmin


# Register your models here.
class AccountAdmin(UserAdmin):
    model = Account
    add_form = AccountCreationForm

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Дополнительные поля',
            {
                'fields': (
                    'phone_number',
                    'about',
                    'profile_pic',
                )
            }
        )
    )

admin.site.register(Account, AccountAdmin)
admin.site.register(Order)
admin.site.register(Wallet)
