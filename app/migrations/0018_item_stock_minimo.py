# Generated by Django 5.0.4 on 2024-05-27 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_item_usuario_registro_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='stock_minimo',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
