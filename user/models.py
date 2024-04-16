from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    picture = models.ImageField(default='perfil.png', upload_to='user/')
    PREGUNTA_RECUPERACION_CHOICES = [
        ('color', 'Color favorito'),
        ('animal', 'Animal favorito'),
        ('apodo', 'Apodo de la infancia'),
    ]
    pregunta_recuperacion = models.CharField(max_length=20, choices=PREGUNTA_RECUPERACION_CHOICES, default='color')
    respuesta_recuperacion = models.TextField(max_length=400, null=True, blank=True)