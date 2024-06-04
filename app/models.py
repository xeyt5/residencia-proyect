from django.db import models
from django.db.models.signals import post_save, pre_delete, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from user.models import User

class Type(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Location(models.Model):
    equipo = models.CharField(max_length=100)
    nivel = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)

    def __str__(self):
        return self.equipo

class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def delete(self, *args, **kwargs):
        self._usuario = kwargs.pop('usuario', None)
        self._descripcion_personalizada = kwargs.pop('descripcion_personalizada', '')
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    telefono = models.CharField(max_length=20)
    correo = models.EmailField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def delete(self, *args, **kwargs):
        self._usuario = kwargs.pop('usuario', None)
        self._descripcion_personalizada = kwargs.pop('descripcion_personalizada', '')
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.nombre
    

class Item(models.Model):
    nombre = models.CharField(max_length=60, null=False, verbose_name='nombre')
    contenido = models.IntegerField(null=False)
    unidad_de_medida = models.CharField(max_length=30, null=False, verbose_name='unidad_medida')
    stock = models.IntegerField(default=0, blank=True)
    stock_minimo = models.IntegerField(default=0, blank=True)  # Campo agregado
    types = models.ManyToManyField(Type, related_name='items')
    locations = models.ManyToManyField(Location, related_name='items')
    marcas = models.ManyToManyField(Marca, related_name='items')
    proveedores = models.ManyToManyField(Proveedor, related_name='items')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


    def delete(self, *args, **kwargs):
        self._usuario = kwargs.pop('usuario', None)
        self._descripcion_personalizada = kwargs.pop('descripcion_personalizada', '')
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.nombre



class Registro(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cod_barras = models.CharField(max_length=100)
    no_referencia_inv = models.CharField(max_length=100)
    fecha_caducidad = models.DateField(null=True, blank=True)
    lote = models.CharField(max_length=100)
    fecha_recepcion = models.DateField()
    cantidad = models.IntegerField(blank=False, null=False)
    cod = models.CharField(max_length=100)
    status = models.IntegerField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.cod_barras

    def save(self, *args, **kwargs):
        # Si el registro ya existe, ajusta el stock restando la cantidad anterior
        if self.pk is not None:
            registro_previo = Registro.objects.get(pk=self.pk)
            diferencia_cantidad = self.cantidad - registro_previo.cantidad
            self.item.stock += diferencia_cantidad
        else:
            self.item.stock += self.cantidad
        self.item.save()
        super(Registro, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.item.stock -= self.cantidad
        self.item.save()
        super(Registro, self).delete(*args, **kwargs)


class Receta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    ingredientes_items = models.ManyToManyField(Item, through='RecetaItem')
    ingredientes_recetas = models.ManyToManyField('self', symmetrical=False, through='RecetaReceta', related_name='subrecetas')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre

class RecetaItem(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    def __str__(self):
        return f'{self.cantidad} de {self.item} en {self.receta}'

class RecetaReceta(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='receta_principal')
    subreceta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name='receta_secundaria')
    cantidad = models.IntegerField()
    
    def __str__(self):
        return f'{self.cantidad} de {self.subreceta} en {self.receta}'





class Bitacora(models.Model):
    accion = models.CharField(max_length=50)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    modelo = models.CharField(max_length=100)
    instancia_id = models.IntegerField(null=True, blank=True)
    descripcion = models.TextField()

    @property
    def fecha(self):
        return self.fecha_hora.date()

    @property
    def hora(self):
        return self.fecha_hora.time()
    


@receiver(post_save, sender=Item)
def registrar_cambio_item(sender, instance, created, **kwargs):
    accion = 'Crear' if created else 'Actualizar'
    if created:
        Bitacora.objects.create(
            accion=accion,
            usuario=instance.usuario,
            modelo='Item',
            instancia_id=instance.id,
            descripcion=f'Se {accion.lower()} el item con ID {instance.id} y nombre {instance.nombre}'
        )

@receiver(post_delete, sender=Item)
def registrar_eliminacion_item(sender, instance, **kwargs):
    usuario = getattr(instance, '_usuario', None)
    descripcion_personalizada = getattr(instance, '_descripcion_personalizada', '')

    if usuario is None and instance.usuario:
        usuario = instance.usuario

    Bitacora.objects.create(
        accion='Eliminar',
        usuario=usuario,
        modelo='Item',
        instancia_id=instance.id,
        descripcion=descripcion_personalizada
    )
        
@receiver(pre_save, sender=Item)
def registrar_actualizacion_item(sender, instance, **kwargs):
    if instance.pk:  # Verifica si el objeto ya existe en la base de datos (es una actualización)
        old_instance = Item.objects.get(pk=instance.pk)
        if instance.nombre != old_instance.nombre or instance.contenido != old_instance.contenido or instance.unidad_de_medida != old_instance.unidad_de_medida:
            Bitacora.objects.create(
                accion='Actualizar',
                usuario=instance.usuario,
                modelo='Item',
                instancia_id=instance.id,
                descripcion=f'Se actualizó el item con ID {instance.id} y nombre {instance.nombre}'
            )
            
         
@receiver(post_save, sender=Marca)
def registrar_cambio_marca(sender, instance, created, **kwargs):
    if created:
        Bitacora.objects.create(
            accion='Crear',
            usuario=instance.usuario,
            modelo='Marca',
            instancia_id=instance.id,
            descripcion=f'Se creó la marca con ID {instance.id} y nombre {instance.nombre}'
        )

@receiver(post_delete, sender=Marca)
def registrar_eliminacion_marca(sender, instance, **kwargs):
    usuario = getattr(instance, '_usuario', None)
    descripcion_personalizada = getattr(instance, '_descripcion_personalizada', '')
    
    if usuario is None and instance.usuario:
        usuario = instance.usuario

    Bitacora.objects.create(
        accion='Eliminar',
        usuario=usuario,
        modelo='Marca',
        instancia_id=instance.id,
        descripcion=descripcion_personalizada
    )

@receiver(post_save, sender=Proveedor)
def registrar_cambio_provedor(sender, instance, created, **kwargs):
    if created:
        Bitacora.objects.create(
            accion='Crear',
            usuario=instance.usuario,
            modelo='Proveedor',
            instancia_id=instance.id,
            descripcion=f'Se creó el proveedor con ID {instance.id} y nombre {instance.nombre}'
        )

@receiver(post_delete, sender=Proveedor)
def registrar_eliminacion_proveedor(sender, instance, **kwargs):
    usuario = getattr(instance, '_usuario', None)
    descripcion_personalizada = getattr(instance, '_descripcion_personalizada', '')
    
    if usuario is None and instance.usuario:
        usuario = instance.usuario
    
    Bitacora.objects.create(
        accion='Eliminar',
        usuario=usuario,
        modelo='Proveedor',
        instancia_id=instance.id,
        descripcion=descripcion_personalizada
    )


    
@receiver(post_save, sender=Registro)
def registrar_cambio_registro(sender, instance, created, **kwargs):
    accion = 'Crear' if created else 'Actualizar'
    if created:
        Bitacora.objects.create(
            accion=accion,
            usuario=instance.usuario,
            modelo='Registro',
            instancia_id=instance.id,
            descripcion=f'Se {accion.lower()} el Registro con ID {instance.id} y con codigo de barras {instance.cod_barras}'
        )
    else:
        Bitacora.objects.create(
            accion=accion,
            usuario=instance.usuario,
            modelo='Registro',
            instancia_id=instance.id,
            descripcion=f'Se {accion.lower()} el registro {instance.id} y con codigo de barras {instance.cod_barras}'
        )

