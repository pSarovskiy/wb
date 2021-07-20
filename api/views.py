import json

from django.core import serializers
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from product.forms import ProductForm
from product.models import Product, Price
from wildberries.functions import image_upload_path, Wosminog


class ProductList(View):
    model = Product

    def get(self, request, *args, **kwargs):
        items = self.model.objects.prices()
        items_down = []
        items_up = []
        items_old = []

        for item in items:
            prices = []
            for price in item.prices.all():
                prices.append({'pk': price.pk, 'pub_date': price.pub_date, 'price': price.price})

            items_data = {
                'pk': item.pk,
                'views': item.is_views,
                'fields': {
                    'pk': item.pk, 'title': item.title, 'url': item.url, 'content': item.content,
                    'start_price': item.start_price, 'price': item.price, 'old_price': item.old_price,
                    'image': item.image, 'edit_date': item.edit_date
                },
                'prices': prices
            }

            if item.price_down and item.start_price != item.price and item.price != 0:
                items_down.append(items_data)
            elif item.price_up and item.start_price != item.price and item.price != 0:
                items_up.append(items_data)
            else:
                items_old.append(items_data)

            # items_list.append({'items': items, 'items_up': items_up, 'items_down': items_down})
        return JsonResponse({'items': {'items': items_old, 'items_up': items_up, 'items_down': items_down}})


def product_delete(request, pk):
    item = Product.objects.get(pk=pk)
    fs = FileSystemStorage()
    if fs.exists(item.image):
        fs.delete(item.image)
    item.delete()
    return JsonResponse({'mess': 'Товар удален...'}, status=201)


def product_views(request, pk):
    item = Product.objects.get(pk=pk)
    item.is_views = False
    item.save()
    return JsonResponse({'mess': 'Товар просмотрен...'}, status=201)


@csrf_exempt
def product_info(request):
    if request.method == "POST":
        request_data = json.loads(request.body)
        if request_data['link'] and 'https://www.wildberries.ru/' in request_data['link']:
            parser = Wosminog()
            parser.url_list = [request_data['link']]
            data = parser.go()
            return JsonResponse({'item': data[0]}, status=201)
    return JsonResponse({'err': 'error'}, status=400)


@csrf_exempt
def product_add(request):
    if request.method == "POST":
        form = ProductForm(json.loads(request.body))
        if form.is_valid():
            product = form.save(commit=False)
            product.published_date = timezone.now()
            data = json.loads(request.body)
            product.title = data['title']
            product.content = data['descr']
            product.start_price = float(data['price'])
            product.price = float(data['price'])
            product.old_price = float(data['price'])
            product.image = image_upload_path(data['image'])
            product.save()
            Price.objects.create(product=product, price=float(data['price']))
            return JsonResponse({'mess': 'Товар теперь отслеживается...'}, status=201)
        return JsonResponse({'err': 'Произошла ошибка при добавлении товара...'}, status=400)
    return JsonResponse({'err': 'Произошла ошибка при отправке запроса...'}, status=400)
