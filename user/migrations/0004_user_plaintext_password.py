# Generated by Django 5.0.4 on 2024-04-17 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_alter_user_respuesta_recuperacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='plaintext_password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]