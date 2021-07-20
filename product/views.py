from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import View

from product.forms import ProductForm
from product.models import Product, Price

from wildberries.functions import image_upload_path, Wosminog


class List(View):
    model = Product
    template_name = 'product/list.html'

    def get(self, request, *args, **kwargs):
        items = self.model.objects
        context = {
            'items': items,
        }
        return render(request, self.template_name, context)


class Detail(View):
    model = Product
    template_name = 'product/detail.html'

    def get(self, request, *args, **kwargs):
        item = get_object_or_404(self.model.objects, pk=kwargs['pk'])
        context = {
            'item': item,
        }
        return render(request, self.template_name, context)


class Delete(View):
    model = Product

    def get(self, request, *args, **kwargs):
        item = self.model.objects.get(pk=kwargs['pk'])
        fs = FileSystemStorage()
        if fs.exists(item.image):
            fs.delete(item.image)
        item.delete()
        return redirect('product-list')


def product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.published_date = timezone.now()
            parser = Wosminog()
            parser.url_list = [form.cleaned_data['url']]
            data = parser.go()
            data = data[0]
            product.title = data['title']
            product.content = data['descr']
            product.price = float(data['price'])
            product.image = image_upload_path(data['image'])
            product.save()
            Price.objects.create(product=product, price=float(data['price']))
            return redirect('product-detail', pk=product.pk)
    else:
        form = ProductForm()
    return render(request, 'product/edit.html', {'form': form})

