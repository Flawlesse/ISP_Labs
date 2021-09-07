from .models import UserAccount
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import (
    AccountSignupForm, AccountLoginForm,
    AccountUpdateForm
)
from proj_helpers.decorators import account_needed, unauthenticated_user


# Create your views here.
@unauthenticated_user(redirect_to='user_accounts:info', fields=('username',))
def signup(request):
    if request.method == 'POST':
        form = AccountSignupForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password2 = form.cleaned_data['password2']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            new_user = User.objects.create_user(
                username,
                email,
                password2
            )
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()

            account = form.save(commit=False)
            account.user = new_user
            account.save()
            return redirect('user_accounts:login')
    else:
        form = AccountSignupForm()
    return render(
        request,
        'user_accounts/signup_page.html',
        {'form': form}
    )


@unauthenticated_user(redirect_to='user_accounts:info', fields=('username',))
def account_login(request):
    print("Current request path:", request.get_full_path())
    if request.method == 'POST':
        form = AccountLoginForm(request.POST)
        print(request.POST)
        print("Current user: ", request.user)
        user = form.get_user()
        print("Recently authenticated user: ", user)
        if user is not None and user.is_active:
            login(request, user)
            return redirect(
                'user_accounts:info',
                username=user.username
            )
    else:
        form = AccountLoginForm()
    return render(
        request,
        'user_accounts/login_page.html',
        {'form': form}
    )


@login_required(login_url='/accounts/login')
@account_needed
def account_logout(request, username):
    print("Request path before logout:", request.get_full_path())
    if request.user.username == username:
        logout(request)
    print("Request path after logout:", request.get_full_path())
    return redirect('index')


def info(request, username):
    # this could be not our account
    account = get_object_or_404(UserAccount, user__username=username)
    can_edit = request.user.username == username
    return render(
        request,
        'user_accounts/account_detail.html',
        {'account': account, 'can_edit': can_edit}
    )


@login_required(redirect_field_name="/accounts/login")
@account_needed
def update(request, username):
    user = request.user
    account = UserAccount.objects.get(user=user)
    if user.username != username:
        return redirect('user_accounts:info', username=username)

    if request.method == 'POST':
        form = AccountUpdateForm(
            request.POST, request.FILES,
            instance=account, request=request
        )
        if form.is_valid():
            # since we know the requset.user is account.user
            # we can just pick the one from request
            print("Form is valid!")
            account = form.save(commit=False)
            user.username = form.cleaned_data['username']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            account.save()
            print(account.profile_pic.url)
            return redirect('user_accounts:info', username=user.username)
    else:
        userdata = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        form = AccountUpdateForm(
            instance=account, initial=userdata,
            request=request
        )
    return render(
        request,
        'user_accounts/account_update.html',
        {'form': form}
    )


@login_required(login_url='/accounts/login')
@account_needed
def delete(request, username):
    if request.user.username == username:
        request.user.delete()
    return redirect("user_accounts:login")
