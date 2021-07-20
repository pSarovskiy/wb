import math
import random
import time

from wildberries.wsgi import *

from django.template.defaultfilters import pluralize
from django.utils import timezone
from wildberries.functions import send_mess_vk, Wosminog
from product.models import Product, Price


def func_chunks_num(lst, c_num):
    n = math.ceil(len(lst) / c_num)
    for x in range(0, len(lst), n):
        e_c = lst[x: n + x]
        yield e_c


def update_price():
    items = Product.objects.all()
    items_list = [item.url for item in items]
    # items_list = list(func_chunks_num(items_list, len(items_list) / 4))
    # for urls_list in items_list:
    parser = Wosminog()
    parser.url_list = items_list
    product_data = parser.go()
    update_count = 0
    items_count = len(items)
    if not product_data:
        print('Нет данных от Wildberries')
        return False
    for i, item in enumerate(items):
        item_data = product_data[i]

        if item.url != item_data['url']:
            continue

        data_price = float(item_data['price']) or 0
        if item.price != data_price:
            if item.price < data_price:
                item.price_up = True
                item.price_down = False
            elif item.price > data_price:
                item.price_up = False
                item.price_down = True
            item.is_views = True
            item.old_price = item.price
            item.price = data_price
            item.save()
            Price.objects.create(product=item, price=float(item_data['price']))
            update_count += 1
    # send_mess_vk()
    print(f'Провере{pluralize(items_count, "н,ны")} {items_count} това{pluralize(items_count, "p,pов")}')
    print(f'Обновле{pluralize(update_count, "н,ны")} {update_count} това{pluralize(update_count, "р,ров")}')


def get_update_price():
    while True:
        print(timezone.now())
        print('Данные обновляются...')
        update_price()
        print(timezone.now())
        print('= = = = = = = = = =')
        time.sleep(10 * 60)


if __name__ == "__main__":
    pass
