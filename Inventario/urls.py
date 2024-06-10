"""
URL configuration for Inventario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app import views
from django.conf import settings
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('salir/', views.salir, name="salir"),
    path('recuperar-contraseña/', views.recuperar_contraseña, name='recuperar_contraseña'),
    path('inventario/', views.inventario),
    path('bitacora/', views.bitacora, name='bitacora'),
    path('marca/', views.marca, name='marca'),
    path('registro-marca/', views.marcaregistro, name='marcaregistro'),
    path('editar-marca/<int:marca_id>/', views.editar_marca, name='editar_marca'),
    path('eliminar-marca/<int:marca_id>/', views.eliminar_marca, name='eliminar_marca'),
    path('proveedores/', views.provedores),
    path('proveedores-registro/', views.proveedoresregistro, name="r_proveedor"),
    path('editar-proveedor/<int:proveedor_id>/', views.editar_proveedor, name='editar_proveedor'),
    path('eliminar-proveedor/<int:proveedor_id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('insertar/', views.registrar_item, name='insertar_r'),
    path('eliminar_registro/<int:registro_id>/', views.eliminar_registro, name='eliminar_registro'),
    path('editar_registro/<int:registro_id>/', views.editar_registro, name='editar_registro'),
    path('asignar-permisos/', views.asignar_permisos, name='asignar_permisos'),
    path('perfil/', views.perfil, name='perfil'),
    path('acerca/', views.acerca, name='acerca'),
    path('registro/', views.registro, name='registro'),
    path('listar-items/', views.listar_items, name='listar_items'),
    path('crear-item/', views.crear_item, name='crear_item'),
    path('eliminar-item/<int:item_id>/', views.eliminar_item, name='eliminar_item'),
    path('editar-item/<int:item_id>/', views.editar_item, name='editar_item'),
    path('recetas/', views.recetas, name='recetas'),
    path('recetas_edit/', views.Recetas_editar, name='recetas_edit'),
    path('registrar-receta/', views.Recetas_registrar, name='registrar_receta')
    
]

if settings.DEBUG: 
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    