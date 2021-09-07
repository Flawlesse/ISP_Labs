from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from proj_helpers.uuid_model import AbstractUUIDModel
from proj_helpers.upload_funcs import upload_images_to
from proj_helpers.custom_validators import phone_validator, password_validator
# from django.core.files import File
# from io import BytesIO
# from PIL import Image
from decimal import Decimal
from django.conf import settings


# Create your models here.
class Wallet(AbstractUUIDModel):
    money = models.DecimalField(
        default=Decimal('100.00'),
        max_digits=9,
        decimal_places=2,
        null=False,
        blank=True,
        validators=[MinValueValidator('0.01')]
    )
    name = models.CharField(
        max_length=40,
        unique=True,
        null=False,
        blank=False
    )
    password = models.CharField(
        max_length=40,
        null=False,
        blank=False,
        validators=[password_validator]
    )


class UserAccount(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        editable=False,
        related_name='account',
        primary_key=True
    )
    phone_number = models.CharField(
        validators=[phone_validator],
        max_length=17,
        blank=True
    )
    about = models.TextField(blank=True)
    profile_pic = models.\
        ImageField(upload_to=upload_images_to, blank=True,
                   null=True, default=settings.DEFAULT_IMAGE_URL)
    wallets = models.ManyToManyField(Wallet, editable=False)
    orders_executed = models.IntegerField(
        default=0,
        editable=False,
        null=False
    )

    def get_image_url(self):
        if self.profile_pic:
            return self.profile_pic.url
        return settings.DEFAULT_IMAGE_URL

    def __str__(self):
        return self.user.username
