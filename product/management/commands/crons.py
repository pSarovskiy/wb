from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from wildberries.cron import get_update_price


class Command(BaseCommand):
    help = 'Парсит и обновляет данные товаров'

    def handle(self, *args, **options):
        get_update_price()
