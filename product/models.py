from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse


class ProductQuerySet(models.QuerySet):
    def prices(self):
        return self.prefetch_related('prices')


class Product(models.Model):
    title = models.CharField('Заголовок', blank=True, editable=False, max_length=180, default='')
    image = models.CharField('Изображение', blank=True, editable=False, max_length=250, default='')
    url = models.CharField('Url', max_length=191, db_index=True, unique=True)
    pub_date = models.DateTimeField('Дата создания', editable=False, auto_now_add=True, db_index=True)
    edit_date = models.DateTimeField('Дата редактирования', auto_now=True, blank=True)
    start_price = models.PositiveIntegerField('Начальная цена', blank=True, editable=False, db_index=True, default=0)
    price = models.PositiveIntegerField('Цена', blank=True, editable=False, db_index=True, default=0.00)
    old_price = models.PositiveIntegerField('Старая цена', blank=True, editable=False, db_index=True, default=0.00)
    content = models.TextField('Описание', editable=False, blank=True, default='')
    price_down = models.BooleanField('Подешевел', editable=False, default=False, db_index=True)
    price_up = models.BooleanField('Подорожал', editable=False, default=False, db_index=True)
    is_views = models.BooleanField('Просмотрено', editable=False, default=False)

    objects = ProductQuerySet.as_manager()

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.title}' or f'{self.url}'

    class Meta:
        db_table = 'product'
        ordering = ['-edit_date']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Price(models.Model):
    product = models.ForeignKey(Product, related_name="prices", editable=False, on_delete=models.CASCADE)
    pub_date = models.DateTimeField('Дата создания', editable=False, auto_now_add=True, db_index=True)
    price = models.PositiveIntegerField('Цена', editable=False, db_index=True)

    def save(self, *args, **kwargs):
        super(Price, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.product}'

    class Meta:
        db_table = 'price'
        ordering = ['pub_date']
        verbose_name = 'Цена'
        verbose_name_plural = 'Цены'


@receiver(pre_save, sender=Product)
def product_pre_save(sender, instance, **kwargs):
    pass


@receiver(post_save, sender=Product, weak=False)
def product_post_save(sender, instance, **kwargs):
    pass


@receiver(pre_delete, sender=Product)
def product_post_save(sender, instance, **kwargs):
    pass
