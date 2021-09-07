from django.http.response import HttpResponse
from proj_helpers.decorators import account_needed, user_is_author
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import Order
from proj_helpers.order_helpers import (
    get_permissions_for_orders, update_orders_info
)
from .forms import OrderCreateForm, OrderUpdateForm


# Create your views here.
def show(request):
    # filter it out later
    order_list = Order.objects.all().order_by('date_posted')
    paginator = Paginator(order_list, 3)  # Show 3 per page.
    page_num = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_num)
    update_orders_info(
        order_list[(page_num - 1) * 3: page_num * 3]
    )
    perms = get_permissions_for_orders(
        order_list[(page_num - 1) * 3: page_num * 3],
        request
    )
    return render(
        request,
        'orders/order_list.html',
        {'page_obj': page_obj, 'permissions': perms}
    )


@login_required(login_url='/accounts/login')
@account_needed
def create(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('orders:detail', order_uuid=order.id)
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order_create.html', {'form': form})


def detail(request, order_uuid):
    order = get_object_or_404(Order, id=order_uuid)
    update_orders_info(list(order))
    perm = get_permissions_for_orders(list(order), request)[0]
    return render(
        request,
        'orders/order_detail.html',
        {'order': order,
         'can_edit_order': perm['can_edit_order'],
         'can_accept_order': perm['can_accept_order'],
         'can_pick_executor_wallet': perm['can_pick_executor_wallet'],
         'can_pick_orderer_wallet': perm['can_pick_orderer_wallet']}
    )


@login_required(login_url='/accounts/login')
@account_needed
@user_is_author(redirect_to='index')
def update(request, order_uuid):
    order = get_object_or_404(Order, id=order_uuid)
    update_orders_info(list(order))
    perm = get_permissions_for_orders(list(order), request)[0]
    if not perm['can_edit_order']:
        return redirect('orders:detail', order_uuid=order_uuid)

    if request.method == 'POST':
        form = OrderUpdateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('orders:detail', order_uuid=order_uuid)
    else:
        order_data = {
            'title': order.title,
            'description': order.description,
            'date_posted': order.date_posted,
            'price': order.price
        }
        form = OrderUpdateForm(initial=order_data)
    return render(
        request,
        'orders/order_update.html',
        {'form': form}
    )


@login_required(login_url='/accounts/login')
@account_needed
@user_is_author(redirect_to='index')
def delete(request, order_uuid):
    order = get_object_or_404(Order, id=order_uuid)
    perm = get_permissions_for_orders(list(order), request)[0]
    if not perm['can_edit_order']:
        return redirect('orders:detail', order_uuid=order_uuid)
    order.delete()
    return redirect('index')


@login_required(login_url='/accounts/login')
@account_needed
def accept(request, order_uuid):
    order = get_object_or_404(Order, id=order_uuid)
    perm = get_permissions_for_orders(list(order), request)[0]
    if not perm['can_accept_order']:
        return redirect('index')
    order.executor = request.user
    return redirect('index')


@login_required(login_url='/accounts/login')
@account_needed
def pick_executor_wallet(request, order_uuid):
    return HttpResponse('')


@login_required(login_url='/accounts/login')
@account_needed
@user_is_author(redirect_to='index')
def pick_orderer_wallet(request, order_uuid):
    return HttpResponse()


@login_required(login_url='/accounts/login')
@account_needed
@user_is_author(redirect_to='index')
def pay_and_delete(request, order_uuid):
    pass
