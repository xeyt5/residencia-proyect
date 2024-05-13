from django.db import models
    
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

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    telefono = models.CharField(max_length=20)
    correo = models.EmailField()
    url = models.URLField()

    def __str__(self):
        return self.nombre
    
class Item(models.Model):
    nombre = models.CharField(max_length=60, null=False, verbose_name='nombre')
    contenido = models.IntegerField(null=False)
    unidad_de_medida = models.CharField(max_length=30, null=False, verbose_name='unidad_medida')
    stock = models.IntegerField()
    types = models.ManyToManyField(Type, related_name='items')
    locations = models.ManyToManyField(Location, related_name='items')
    marcas = models.ManyToManyField(Marca, related_name='items')
    proveedores = models.ManyToManyField(Proveedor, related_name='items')

    def __str__(self):
        return self.nombre
    
class Registro(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE)
    cod_barras = models.CharField(max_length=100)
    no_referencia_inv = models.CharField(max_length=100)
    fecha_caducidad = models.DateField(null=True, blank=True)
    lote = models.CharField(max_length=100)
    fecha_recepcion = models.DateField()
    cantidad = models.IntegerField()
    cod = models.CharField(max_length=100)
    status = models.IntegerField()
    
    def __str__(self):
        return self.cod_barras
 
    
