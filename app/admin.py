from django.contrib import admin
from .models import Registro, Item, Location, Type, Proveedor, Marca

admin.site.register(Item)
admin.site.register(Registro)
admin.site.register(Location)
admin.site.register(Type)
admin.site.register(Proveedor)
admin.site.register(Marca)