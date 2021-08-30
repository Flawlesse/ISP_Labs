from .models import UserAccount
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import (
    AccountSignupForm, AccountLoginForm,
    AccountDetailForm, AccountUpdateForm
)


# Create your views here.
def signup(request):
    context = {'signup_form': AccountSignupForm()}
    if request.method == 'POST':
        form = AccountSignupForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password2 = form.cleaned_data['password2']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            print(form.cleaned_data)

            new_user = User.objects.create_user(
                username,
                email,
                password2
            )
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()

            account = form.save()
            account.user = new_user
            account.save()
            return redirect('user_accounts:login')
        context = {'signup_form': form}
    return render(
        request,
        'user_accounts/signup_page.html',
        context
    )


def account_login(request):  # rewrite
    # if request.user.is_authenticated:
    #     return redirect(
    #         'user_accounts:info',
    #         username=request.user.username
    #     )

    if request.method == 'POST':
        form = AccountLoginForm(
            request=request,
            data=request.POST)
        if form.is_valid():
            print('Form is valid!')
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect(
                    'user_accounts:info',
                    username=user.username
                )
        return redirect('user_accounts:login')
    return render(
        request,
        'user_accounts/login_page.html',
        {'login_form': AccountLoginForm()}
    )


@login_required(login_url='accounts/login')
def account_logout(request, username):
    if request.user.username == username:
        logout(request)
    return redirect('user_accounts:login')


def info(request, username):  # rewrite!!!
    # this could be not our account
    account = get_object_or_404(UserAccount, user__username=username)
    return render(
        request,
        'user_accounts/account_detail.html',
        {'detail_form': AccountDetailForm(instance=account)}
    )


@login_required(login_url="accounts/login")
def update(request, username):
    user = request.user
    account = UserAccount.objects.get(user=user)
    if user.username != username:
        return redirect('user_accounts:info', username=username)
    if request.method == 'POST':
        form = AccountUpdateForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()
        return redirect('user_accounts:info', username=username)
    return render(
        request,
        'user_accounts/account_detail.html',
        {'update_form': AccountUpdateForm(instance=account)}
    )


@login_required(login_url='accounts/login')
def delete(request, username):
    user = request.user
    if user.username == username:
        account = UserAccount.objects.get(user__username=username)
        account.user.delete()
        account.delete()
    return redirect("user_accounts:login")
