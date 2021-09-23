from .order_state import OrderState


def get_permissions_for_order(order, request):
    "Возвращает разрешения для заказа, основываясь на текущем запросе."
    
    perms = {}
    perms['can_edit'] = (
        order.get_state() == OrderState.FREE and
        request.user.is_authenticated and
        request.user.username == order.author.username
    )
    perms['can_accept'] = (
        order.get_state() == OrderState.FREE and
        request.user.is_authenticated and
        not hasattr(request.user, 'current_order') and
        request.user.username != order.author.username
    )
    perms['can_reject'] = (
        order.get_state() != OrderState.FREE and
        request.user.is_authenticated and
        hasattr(request.user, 'current_order') and
        request.user.current_order.id == order.id
    )
    perms['can_pick_ord_wallet'] = (
        request.user.is_authenticated and
        request.user.username == order.author.username
    )
    perms['can_pick_exec_wallet'] = (
        order.get_state() != OrderState.FREE and
        request.user.is_authenticated and
        request.user.username == order.executor.username
    )
    perms['can_pay_and_delete'] = (
        order.get_state() == OrderState.OK and
        request.user.is_authenticated and
        request.user.username == order.author.username
    )
    return perms
