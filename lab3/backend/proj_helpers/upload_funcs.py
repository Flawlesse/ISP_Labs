import os
import datetime


def _set_filename_format(now, instance, filename):
    """
    {username}-{date}-{microsecond}{extension}
    akado-2021-07-12-158859.png
    """
    return "{username}-{date}-{microsecond}{extension}".format(
        username=instance.username,
        date=str(now.date()),
        microsecond=now.microsecond,
        extension=os.path.splitext(filename)[1],
    )


def _user_directory_path(instance, filename):
    """
    images/{year}/{month}/{day}/{filename}
    images/2021/7/12/hjh/hjh-2016-07-12-158859.png
    """
    now = datetime.datetime.now()

    path = "{year}/{month}/{day}/{filename}".format(
        year=now.year,
        month=now.month,
        day=now.day,
        filename=_set_filename_format(now, instance, filename),
    )

    return path


def upload_images_to(instance, filename):
    return f'uploads/images/{instance.username}/' +\
        f'{_user_directory_path(instance, filename)}'
