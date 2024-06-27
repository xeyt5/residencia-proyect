# Generated by Django 5.0.4 on 2024-06-27 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_usoreceta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='contenido',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Contenido'),
        ),
        migrations.AlterField(
            model_name='item',
            name='nombre',
            field=models.CharField(max_length=60, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='item',
            name='stock',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='Stock'),
        ),
        migrations.AlterField(
            model_name='item',
            name='stock_minimo',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, verbose_name='Stock mínimo'),
        ),
        migrations.AlterField(
            model_name='item',
            name='unidad_de_medida',
            field=models.CharField(max_length=30, verbose_name='Unidad de medida'),
        ),
    ]