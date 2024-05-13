from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    picture = models.ImageField(default='perfil.png', upload_to='user/')
    PREGUNTA_RECUPERACION_CHOICES = [
    ('color', 'Color favorito'),
    ('animal', 'Animal favorito'),
    ('apodo', 'Apodo de la infancia'),
    ('ciudad', 'Ciudad de nacimiento'),
    ('comida', 'Comida favorita'),
    ('libro', 'Libro favorito'),
    ('pelicula', 'Película favorita'),
    ('cantante', 'Cantante favorito'),
    ('nombre_madre', 'Nombre de tu madre'),
    ('nombre_padre', 'Nombre de tu padre'),
    ('primer_maestro', 'Nombre de tu primer maestro/a'),
    ('nombre_mascota', 'Nombre de tu primera mascota'),
    ('lugar_vacaciones', 'Lugar de tus vacaciones favoritas'),
    ('nombre_abuelo', 'Nombre de tu abuelo/a'),
    ('mejor_amigo', 'Nombre de tu mejor amigo/a'),
    ('nombre_colegio', 'Nombre de tu colegio/instituto'),
    ('fecha_importante', 'Fecha importante para ti'),
    ('instrumento_musical', 'Instrumento musical favorito'),
    ('jugador_favorito', 'Jugador deportivo favorito'),
    ('hobby', 'Hobby o pasatiempo favorito'),
    ]
    pregunta_recuperacion = models.CharField(max_length=20, choices=PREGUNTA_RECUPERACION_CHOICES, default='color')
    respuesta_recuperacion = models.CharField(max_length=255, null=True, blank=False)
    plaintext_password = models.CharField(max_length=128, null=True, blank=True)

    def set_password(self, raw_password):
        self.plaintext_password = raw_password
        super().set_password(raw_password)

    def save(self, *args, **kwargs):
        if self.plaintext_password:
            self.set_password(self.plaintext_password)
        super().save(*args, **kwargs)