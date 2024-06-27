# Generated by Django 5.0.4 on 2024-06-27 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0034_alter_item_contenido_alter_item_nombre_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='contenido',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='item',
            name='nombre',
            field=models.CharField(max_length=60, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='item',
            name='stock',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='item',
            name='stock_minimo',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='item',
            name='unidad_de_medida',
            field=models.CharField(max_length=30, verbose_name='unidad_medida'),
        ),
    ]
