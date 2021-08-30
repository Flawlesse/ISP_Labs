from django.contrib.auth.models import User


def upload_images_to(instance: User, filename):
    return f'uploads/images/{instance.username}/{filename}'


def upload_thumbnails_to(instance: User, filename):
    return f'uploads/thumbnails/{instance.username}/{filename}'
