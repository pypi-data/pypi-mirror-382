# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management.base import BaseCommand
from django.utils import termcolors


def print_and_call(command, *args, **kwargs):
    kwargs.setdefault('interactive', True)
    print(termcolors.make_style(fg='cyan', opts=('bold',))('>>> {} {}{}'.format(
        command, ' '.join(args), ' '.join(['{}={}'.format(k, v) for k, v in list(kwargs.items())]))))
    call_command(command, *args, **kwargs)


class Command(BaseCommand):
    def handle(self, *args, **options):

        app_labels = []
        for app_label in settings.INSTALLED_APPS:
            app_labels.append(app_label.split('.')[-1])

        print_and_call('makemigrations', *app_labels)
        print_and_call('migrate')
        if not settings.DEBUG:
            print_and_call('collectstatic', clear=True, verbosity=0, interactive=False)

        if not User.objects.exists():
            user = User.objects.create_superuser('admin')
            password = getattr(settings, 'DEFAULT_PASSWORD', lambda user: '123')(user)
            user.set_password(password)
            user.save()
            print('Superuser "admin" with password "{}" was created.'.format(password))

        if getattr(settings, 'USE_S3'):
            staticfiles_storage.collectstatic()
