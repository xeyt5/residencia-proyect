# Generated by Django 5.0.4 on 2024-04-16 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='pregunta_recuperacion',
            field=models.CharField(choices=[('color', 'Color favorito'), ('animal', 'Animal favorito'), ('apodo', 'Apodo de la infancia')], default='color', max_length=20),
        ),
    ]
