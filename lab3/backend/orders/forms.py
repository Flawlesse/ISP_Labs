from django.contrib.auth.forms import UserCreationForm
from .models import Account


class AccountCreationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = '__all__'
