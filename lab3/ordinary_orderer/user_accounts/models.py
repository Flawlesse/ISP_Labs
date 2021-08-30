from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from proj_helpers.uuid_model import AbstractUUIDModel
from proj_helpers.upload_funcs import upload_images_to, upload_thumbnails_to
from proj_helpers.custom_validators import phone_validator, password_validator
from django.core.files import File
from io import BytesIO
from PIL import Image
from decimal import Decimal


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
        unique=True,
        # strip=False,
        null=False,
        blank=False,
        validators=[password_validator]
    )


class UserAccount(AbstractUUIDModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        editable=False,
        null=True,  # may be BAD
        related_name='account',
    )
    phone_number = models.CharField(
        validators=[phone_validator],
        max_length=17,
        blank=True
    )
    about = models.TextField(blank=True)
    profile_pic = models.\
        ImageField(upload_to=upload_images_to, blank=True,
                   null=True, default='no_pic.jpeg')
    thumbnail = models.\
        ImageField(upload_to=upload_thumbnails_to, blank=True,
                   null=True, editable=False)
    wallets = models.ManyToManyField(Wallet, editable=False)
    orders_executed = models.IntegerField(
        default=0,
        editable=False,
        null=False
    )

    def get_image(self):
        if self.profile_pic:
            # return 'http://127.0.0.1:8000' + self.profile_pic.url
            return self.profile_pic.url
        return ''

    def get_thumbnail(self):
        if self.profile_pic:
            self.thumbnail = self.make_thumbnail(self.profile_pic)
            self.save()
            # return 'http://127.0.0.1:8000' + self.thumbnail.url
            return self.thumbnail.url
        else:
            return ''

    def make_thumbnail(self, image, size=(200, 200)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail

    def __str__(self):
        return self.user.username
