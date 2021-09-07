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
        required=False
    )
    last_name = forms.CharField(
        label='Ваша фамилия:',
        max_length=150,
        required=False
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
            'email',  # NO IN UPDATE
            'password1',  # NO IN UPDATE
            'password2',  # NO IN UPDATE
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


class AccountLoginForm(forms.Form):
    username = forms.CharField(
        label='Логин:',
        max_length=40,
        validators=[username_validator],
    )
    password = forms.CharField(
        widget=forms.PasswordInput(),
        label='Пароль:',
        strip=False,
        validators=[password_validator]
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            UserAccount.objects.get(user__username=username)
        except UserAccount.DoesNotExist:
            print("Аккаунта с таким именем пользователя не существует.")
            raise ValidationError(
                "Аккаунта с таким именем пользователя не существует."
            )
        return username

    # this goes after clean_username()
    def clean_password(self):
        password = self.cleaned_data['password']
        try:
            username = self.cleaned_data['username']
        except KeyError:
            return password
        user = User.objects.get(username=username)
        if not user.check_password(password):
            print("Неверный пароль от аккаунта.")
            raise ValidationError(
                "Неверный пароль от аккаунта."
            )
        return password

    def get_user(self):
        if self.is_valid():
            print('Form is valid!')
            return User.objects.get(username=self.cleaned_data['username'])
        else:
            print('Form is INvalid!')
            return None


class AccountUpdateForm(AccountSignupForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields.pop('password1')
        self.fields.pop('password2')
        self.fields.pop('email')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
            print("User:", user)
            if (self.request.user.username == username):
                # we want to keep data unchanged too
                raise User.DoesNotExist
            raise ValidationError(
                "Пользователь с таким именем уже существует!"
            )
        except User.DoesNotExist:
            pass
        return username
