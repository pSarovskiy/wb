# Generated by Django 3.2.4 on 2021-06-19 06:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.CharField(blank=True, default='', editable=False, max_length=250, verbose_name='Изображение'),
        ),
        migrations.AlterField(
            model_name='price',
            name='price',
            field=models.DecimalField(db_index=True, decimal_places=2, editable=False, max_digits=6, verbose_name='Цена'),
        ),
        migrations.RemoveField(
            model_name='price',
            name='product',
        ),
        migrations.AddField(
            model_name='price',
            name='product',
            field=models.ForeignKey(default='', editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='product.product'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(blank=True, default='', editable=False, max_length=180, verbose_name='Заголовок'),
        ),
        migrations.AlterField(
            model_name='product',
            name='url',
            field=models.CharField(db_index=True, max_length=191, unique=True, verbose_name='Url'),
        ),
    ]
