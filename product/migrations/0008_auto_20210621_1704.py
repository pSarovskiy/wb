# Generated by Django 3.2.4 on 2021-06-21 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_auto_20210619_0905'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='old_price',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, default=0.0, editable=False, max_digits=6, verbose_name='Старая цена'),
        ),
        migrations.AddField(
            model_name='product',
            name='price_down',
            field=models.BooleanField(db_index=True, default=False, editable=False, verbose_name='Подешевел'),
        ),
        migrations.AddField(
            model_name='product',
            name='price_up',
            field=models.BooleanField(db_index=True, default=False, editable=False, verbose_name='Подорожал'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=2, default=0.0, editable=False, max_digits=6, verbose_name='Цена'),
        ),
    ]