from orders.models import Wallet, Order
from django.db.models import F


class TransactionError(Exception):
    pass


class Transaction:
    def __init__(self, order: Order):
        self.wallet_from = order.orderer_wallet
        self.wallet_to = order.executor_wallet
        self.money_to_transfer = order.price
        self.executor = order.executor

    def is_valid(self):
        try:
            if self.wallet_from.money < self.money_to_transfer:
                raise TransactionError(
                    "На кошельке заказчика недостаточно денежных средств."
                    + f"\nСредства: ${self.wallet_from.money}\n"
                    + f"Цена: ${self.money_to_transfer}."
                )
        except TransactionError as e:
            print(e)
            return False
        return True

    def commit(self):
        try:
            self.wallet_from.refresh_from_db()
            self.wallet_to.refresh_from_db()
            self.executor.refresh_from_db()

            self.wallet_from.money = F('money') - self.money_to_transfer
            self.wallet_to.money = F('money') + self.money_to_transfer
            self.executor.orders_executed = F('orders_executed') + 1

            self.wallet_to.save()
            self.wallet_from.save()
            self.executor.save()
        except Wallet.DoesNotExist:
            raise TransactionError(
                "\nПроизошла проблема во время транзакции при обработке заказа."
                + f"\nUUID заказа: {self.order.id}"
                + f"\nСтоимость: ${self.order.price}\n"
            )
