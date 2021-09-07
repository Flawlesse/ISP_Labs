from .order_state import OrderState


def get_permissions_for_orders(order_list, request):
    permissions = []
    for order in order_list:
        can_edit_order = (
            order.get_state() == OrderState.FREE and
            request.user.username == order.author.username
        )
        can_accept_order = (
            order.get_state() == OrderState.FREE and
            request.user.is_authenticated and
            request.user.is_active and
            request.user.username != order.author.username
        )
        can_pick_executor_wallet = (
            order.get_state() in (OrderState.TAKEN, OrderState.READY) and
            request.user.username == order.executor.username
        )
        can_pick_orderer_wallet = (
            order.get_state() in (OrderState.TAKEN, OrderState.READY) and
            request.user.username == order.author.username
        )
        permissions.append({
            'can_edit_order': can_edit_order,
            'can_accept_order': can_accept_order,
            'can_pick_executor_wallet': can_pick_executor_wallet,
            'can_pick_orderer_wallet': can_pick_orderer_wallet
        })
    return permissions


def update_orders_info(orders):
    for order in orders:
        state = order.get_state()
        if state == OrderState.FREE:
            order.executor_wallet = None
            order.orderer_wallet = None
