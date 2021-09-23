from django.db import models
from django.conf import settings
from django.db.models.fields import DecimalField
from proj_helpers.uuid_model import AbstractUUIDModel
from proj_helpers.order_state import OrderState
from django.core.validators import MinValueValidator
from proj_helpers.custom_validators import (
    phone_validator,
    name_validator
)
from proj_helpers.upload_funcs import upload_images_to
from decimal import Decimal
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Wallet(AbstractUUIDModel):
    money = models.DecimalField(
        default=Decimal('100.00'),
        max_digits=9,
        decimal_places=2,
        null=False,
        blank=True,
        validators=[MinValueValidator(
            Decimal('0.01'),
            "На кошельке не может быть меньше 1 цента!"
        )],
    )
    name = models.CharField(
        max_length=40,
        unique=True,
        null=False,
        blank=False,
        validators=[name_validator]
    )
    password = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        editable=False,
    )

    def __str__(self):
        return f'{self.name} ${self.money}'


class Account(AbstractUser):
    email = models.EmailField(unique=True, blank=True, null=False)
    phone_number = models.CharField(
        validators=[phone_validator],
        max_length=17,
        blank=True
    )
    about = models.TextField(blank=True)
    profile_pic = models.ImageField(
        upload_to=upload_images_to, blank=True,
        null=True
    )
    wallets = models.ManyToManyField(
        Wallet,
        editable=False,
        related_name='accounts'
    )
    orders_executed = models.IntegerField(
        default=0,
        editable=False,
        null=False
    )

    def save(self, *args, **kwargs):
        try:
            old_inst = Account.objects.get(id=self.id)
            if old_inst.profile_pic != self.profile_pic:
                old_inst.profile_pic.delete()
        except: 
            pass
        super(Account, self).save(*args, **kwargs)

    def delete(self):
        self.profile_pic.delete()
        return super().delete()

    def get_image_url(self):
        if self.profile_pic:
            return self.profile_pic.url
        return settings.DEFAULT_IMAGE_URL

    def __str__(self):
        return self.username


class Order(AbstractUUIDModel):
    author = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        editable=False,
        null=False
    )
    executor = models.OneToOneField(
        Account,
        null=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name='current_order'
    )
    title = models.CharField(max_length=100, blank=False, null=False, unique=True)
    description = models.TextField(blank=False, null=False)
    date_posted = models.DateTimeField(auto_now_add=True)
    price = DecimalField(
        default=Decimal('5.00'),
        max_digits=6,
        decimal_places=2,
        null=False,
        blank=True,
        validators=[MinValueValidator(
            Decimal('0.01'),
            "Заказ должен стоить хотя бы 1 цент!"
        )],
    )
    orderer_wallet = models.ForeignKey(
        Wallet,
        to_field='id',
        on_delete=models.SET_NULL,
        null=True,
        related_name='author_wallet_orders'
    )
    executor_wallet = models.ForeignKey(
        Wallet,
        to_field='id',
        on_delete=models.SET_NULL,
        null=True,
        related_name='executor_wallet_orders'
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
