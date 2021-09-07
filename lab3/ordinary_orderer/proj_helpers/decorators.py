from django.contrib.auth import logout
from user_accounts.models import UserAccount
from django.http.response import Http404
from django.shortcuts import redirect
from orders.models import Order
import functools


def account_needed(view_func=None):
    """
    !Ставить @login_requied перед данным декоратором!
    Проверка на наличие аккаунта у пользователя, который сделал
    запрос. В случае данного view у пользователя обязан быть
    UserAccount. Если нет, то logout и редирект на главную страницу.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                UserAccount.objects.get(
                    user__username=request.user.username
                )
            except UserAccount.DoesNotExist:
                logout(request)
                return redirect('index')
            return view_func(request, *args, **kwargs)
        return wrapper
    if view_func:
        return decorator(view_func)
    return decorator


def unauthenticated_user(
        view_func=None, redirect_to: str = None, **dec_kwargs
        ):
    """
    !Отображение исключительно для пользователя без аккаунта!
    При необходимости добавьте поля, которые будут необходимы для редиректа, с
    помощью аргумента 'fields=(... , )', где они будут перечислены.
    Поля должны иметь названия, которые являются названиями полей в User,
    вроде fields=('username', 'password', 'first_name'), т.к. эти имена
    будут переданы как redirect('url', **kw{'username': request.user.username,
    ...}).
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                if request.user.is_authenticated:
                    # if you somehow logged in as a user, that has no account,
                    # this throws an error
                    UserAccount.objects.get(
                        user__username=request.user.username
                    )
                    # get all fields passed as keyword argument 'fields'
                    field_names = dec_kwargs.get('fields', tuple())
                    if len(field_names) == 0:
                        return redirect(redirect_to)
                    kw = dict(
                        zip(
                            field_names,
                            [getattr(request.user, f'{name}')
                                for name in field_names]
                        )
                    )
                    return redirect(redirect_to, **kw)
            except UserAccount.DoesNotExist:
                # add error logs
                logout(request)
                print("Пользователь без аккаунта успешно вышел!")
            return view_func(request, *args, **kwargs)
        return wrapper
    if view_func:
        return decorator(view_func)
    return decorator


def user_is_author(view_func=None, redirect_to: str = None):
    """
    !Ставить @account_needed перед данным декоратором!
    Этот декоратор проверяет, является ли пользователь автором заказа (Order).
    По определению автор не может быть AnonymousUser или быть без аккаунта.
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                order_uuid = kwargs.get('order_uuid')
                order = Order.objects.get(id=order_uuid)
                if (order.author.username == request.user.username):
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect(redirect_to)
            except KeyError:
                raise Http404("No 'order_uuid' argument passed in view_func.")
            except Order.DoesNotExist:
                raise Http404("No order with such 'order_uuid' found.")
        return wrapper
    if view_func:
        return decorator(view_func)
    return decorator
