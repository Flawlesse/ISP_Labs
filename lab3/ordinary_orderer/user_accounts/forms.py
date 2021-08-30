from django.contrib.auth.forms import (
    AuthenticationForm,
)
from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from .models import UserAccount
from proj_helpers.custom_validators import (
    username_validator, password_validator
)
from django.contrib.auth.models import User


class AccountSignupForm(ModelForm):
    username = forms.CharField(
        label='Имя пользователя:',
        max_length=40,
        validators=[username_validator],
    )
    email = forms.EmailField(
        label='Ваш e-mail:',
        max_length=254
    )
    first_name = forms.CharField(
        label='Ваше имя:',
        max_length=150,
    )
    last_name = forms.CharField(
        label='Ваша фамилия:',
        max_length=150,
    )
    password1 = forms.CharField(widget=forms.PasswordInput(),
                                label='Введите пароль:',
                                strip=False,
                                validators=[password_validator])
    password2 = forms.CharField(widget=forms.PasswordInput(),
                                label='И ещё раз:',
                                strip=False,
                                validators=[password_validator])

    class Meta:
        model = UserAccount
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'phone_number',
            'about',
            'profile_pic',
        )
        labels = {
            'phone_number': 'Ваш номер телефона:',
            'about': 'Расскажите о себе:',
            'profile_pic': 'Аватар:',
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
            raise ValidationError(
                "Пользователь с таким именем уже существует!"
            )
        except User.DoesNotExist:
            pass
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email=email)
            raise ValidationError(
                "Пользователь с таким e-mail уже существует!"
            )
        except User.DoesNotExist:
            pass
        return email

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError("Ваши пароли не совпадают!")
        return password2


class AccountLoginForm(AuthenticationForm):
    class Meta:
        model = User


# widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
class AccountUpdateForm(AccountSignupForm):
    class Meta(AccountSignupForm.Meta):
        exclude = ('password1', 'password2', 'thumbnail', 'wallets')


class AccountDetailForm(ModelForm):
    class Meta:
        model = UserAccount
        fields = '__all__'
        exclude = ('user', )
