from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.fields import DecimalField
from proj_helpers.uuid_model import AbstractUUIDModel
from proj_helpers.order_state import OrderState
from decimal import Decimal
from user_accounts.models import Wallet
from django.contrib.auth.models import User


# Create your models here.
class Order(AbstractUUIDModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        editable=False,
        null=False
    )
    executor = models.OneToOneField(
        User,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name='current_order'
    )
    title = models.CharField(max_length=100, blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    date_posted = models.DateTimeField(auto_now_add=True)
    price = DecimalField(
        default=Decimal('5.00'),
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    orderer_wallet = models.OneToOneField(
        Wallet,
        to_field='id',
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name='author_order'
    )
    executor_wallet = models.OneToOneField(
        Wallet,
        to_field='id',
        on_delete=models.SET_NULL,
        null=True,
        editable=False,
        related_name='executor_order'
    )

    def get_state(self):
        has_executor = self.executor is not None
        has_exec_wallet = self.executor_wallet is not None
        has_orderer_wallet = self.orderer_wallet is not None

        if not has_executor:
            return OrderState.FREE
        elif not has_exec_wallet:
            return OrderState.TAKEN
        elif not has_orderer_wallet:
            return OrderState.READY
        else:
            return OrderState.OK

    def __str__(self):
        return self.title
