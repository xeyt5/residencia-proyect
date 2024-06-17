from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout, authenticate, login
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth import get_user_model
from django.contrib import messages  
from .models import Item, Registro, Location, Type, Marca, Proveedor, Bitacora, Receta, RecetaItem, RecetaReceta, UsoReceta
from .forms import marcaform, proveedorForm, ItemForm, TypeForm, LocationForm
from django.http import JsonResponse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from io import BytesIO

# Create your views here.

@permission_required('app.view_auth_permission')
@login_required
def asignar_permisos(request):
    usuarios = User.objects.all()

    content_types = ContentType.objects.filter(
        app_label='app',
        model__in=['location', 'marca', 'proveedor', 'item', 'registro']
    )

    permisos = Permission.objects.filter(content_type__in=content_types)

    if request.method == 'POST':
        if 'delete_user' in request.POST:
            username = request.POST.get('username')
            print(f"Username received for deletion: {username}")

            try:
                user_to_delete = User.objects.get(username=username)
                user_to_delete.delete()
                messages.success(request, f"El usuario '{username}' ha sido eliminado.")
            except User.DoesNotExist:
                messages.error(request, f"El usuario '{username}' no existe.")
            
            return redirect('asignar_permisos')

        username = request.POST.get('username')
        print(f"Username received in POST: {username}")

        try:
            selected_user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, f"El usuario '{username}' no existe.")
            return redirect('asignar_permisos')

        permission_ids = request.POST.getlist('permissions')
        selected_user.user_permissions.clear()

        for permission_id in permission_ids:
            permission = Permission.objects.get(id=permission_id)
            selected_user.user_permissions.add(permission)

        print(f"is_active: {request.POST.get('is_active')}")

        is_active = 'is_active' in request.POST
        selected_user.is_active = is_active
        selected_user.save()

        return redirect('asignar_permisos')

    selected_username = request.GET.get('username')
    print(f"Username received in GET: {selected_username}")

    selected_user = User.objects.filter(username=selected_username).first()
    selected_user_permissions = selected_user.user_permissions.all() if selected_user else []

    return render(request, 'asignar_permisos.html', {
        'usuarios': usuarios,
        'permisos': permisos,
        'selected_username': selected_username,
        'selected_user_permissions': selected_user_permissions,
        'selected_user': selected_user
    })
    
    

@permission_required('app.view_auth_permission')
@login_required
def eliminar_usuario(request, username):
    try:
        usuario = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, f"El usuario '{username}' no existe.")
        return redirect('asignar_permisos')

    if request.method == 'POST':
        if request.POST.get('confirmar') == 'true':
            usuario.delete()
            messages.success(request, f"El usuario '{username}' ha sido eliminado.")
        else:
            messages.warning(request, "No se ha eliminado al usuario.")
        return redirect('asignar_permisos')

    return render(request, 'eliminar_usuario.html', {'usuario': usuario})


@login_required
def index(request):
        return render(request, 'index.html')

@login_required
@permission_required('app.view_bitacora')
def bitacora(request):
    registros = Bitacora.objects.all().order_by('-fecha_hora')
    return render(request, 'bitacora.html', {'registros': registros})


permission_required('app.view_marca')
@login_required
def marca(request):
    Marcas = Marca.objects.all()
    return render(request, 'marca.html', {'Marcas':Marcas})


@permission_required('app.delete_marca')
@login_required
def eliminar_marca(request, marca_id):
    marca = get_object_or_404(Marca, id=marca_id)
    if request.method == 'POST':
        descripcion_personalizada = request.POST.get('descripcion_personalizada', '')
        usuario = request.user

        # Llama a delete y pasa los argumentos adicionales
        marca.delete(usuario=usuario, descripcion_personalizada=descripcion_personalizada)

        return JsonResponse({'message': 'Marca eliminada exitosamente', 'usuario': usuario.username})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    
permission_required('app.add_marca')
@login_required
def marcaregistro(request):
    if request.method == 'POST':
        form = marcaform(request.POST)
        if form.is_valid():
            marca = form.save(commit=False)
            marca.usuario = request.user
            marca.save()
            messages.success(request, 'Se agregó la marca correctamente')
            return redirect('marca')  
    else:
        form = marcaform()
    return render(request, 'insertar_marca.html', {'form': form})



@permission_required('app.change_registro')
@login_required
def editar_marca(request, marca_id):
    marca = get_object_or_404(Marca, id=marca_id)
    if request.method == 'POST':
        form = marcaform(request.POST, instance=marca)
        if form.is_valid():
            marca = form.save(commit=False)
            marca.usuario = request.user
            marca.save()

            descripcion_personalizada = request.POST.get('descripcion_personalizada', '')
            if not descripcion_personalizada:
                messages.warning(request, 'No se proporcionó ninguna descripción personalizada.')
                Bitacora.objects.create(
                    accion='Actualizar',
                    usuario=request.user,
                    modelo='Marca',
                    instancia_id=marca.id,
                    descripcion=f''
                )
            else:
                Bitacora.objects.create(
                    accion='Actualizar',
                    usuario=request.user,
                    modelo='Marca',
                    instancia_id=marca.id,
                    descripcion=descripcion_personalizada
                )
                messages.success(request, 'Se editó la marca correctamente con la descripción personalizada.')

            return redirect('marca')
    else:
        form = marcaform(instance=marca)
    return render(request, 'editar_marca.html', {'form': form})
    
    
    
    
permission_required('app.view_Proveedor')  
@login_required
def provedores(request):
    Proveedores = Proveedor.objects.all()
    return render(request, 'proveedores.html', {'Proveedores':Proveedores})  


@permission_required('app.delete_proveedor')
@login_required
def eliminar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        descripcion_personalizada = request.POST.get('descripcion_personalizada', '')
        usuario = request.user

        # Llama a delete y pasa los argumentos adicionales
        proveedor.delete(usuario=usuario, descripcion_personalizada=descripcion_personalizada)

        return JsonResponse({'message': 'Proveedor eliminado exitosamente', 'usuario': usuario.username})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)









permission_required('app.add_Proveedor')
@login_required
def proveedoresregistro(request):
    if request.method == 'POST':
        form = proveedorForm(request.POST)
        if form.is_valid():
            provedor = form.save(commit=False)
            provedor.usuario = request.user
            provedor.save()
            messages.success(request, 'Se registró correctamente el proveedor')
            return redirect('/proveedores/')
    else:
        form = proveedorForm()
    return render(request, 'proveedoresr.html', {'form': form})


@permission_required('app.change_Proveedor')
@login_required
def editar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        form = proveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            proveedor = form.save(commit=False)
            proveedor.usuario = request.user
            proveedor.save()

            descripcion_personalizada = request.POST.get('descripcion_personalizada', '')
            if not descripcion_personalizada:
                messages.warning(request, 'No se proporcionó ninguna descripción personalizada.')
                Bitacora.objects.create(
                    accion='Actualizar',
                    usuario=request.user,
                    modelo='Proveedor',
                    instancia_id=proveedor.id,
                    descripcion=f''
                )
            else:
                Bitacora.objects.create(
                    accion='Actualizar',
                    usuario=request.user,
                    modelo='Proveedor',
                    instancia_id=proveedor.id,
                    descripcion=descripcion_personalizada
                )
                messages.success(request, 'Se modificó correctamente el proveedor con la descripción personalizada.')

            return redirect('/proveedores/')
    else:
        form = proveedorForm(instance=proveedor)
    return render(request, 'editar_proveedor.html', {'form': form})



    
@login_required
def perfil(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Se modificaron tus datos")
            # Autenticar nuevamente al usuario para mantenerlo conectado
            user = authenticate(request, username=user.username)
            if user is not None:
                login(request, user)
                # Save the session to maintain the user's authentication
                request.session.save()
            return redirect('perfil')
    else:
        form = CustomUserChangeForm(instance=user)
    
    return render(request, 'perfil.html', {'form': form})


@permission_required('app.view_registro')
@login_required    
def inventario(request):
    items = Item.objects.all()
    registros = Registro.objects.all()
    types = Type.objects.all()
    locations = Location.objects.all()
    Marcas = Marca.objects.all()
    
    # Pasar la información del stock mínimo
    items_with_stock_minimo = {item.id: item.stock_minimo for item in items}
    
    return render(request, 'inventario.html', {
        'items': items,
        'registros': registros,
        'types': types,
        'locations': locations,
        'Marcas': Marcas,
        'items_with_stock_minimo': items_with_stock_minimo
    })


@permission_required('app.change_registro')
@login_required
def editar_registro(request, registro_id):
    registro = get_object_or_404(Registro, pk=registro_id)
    item = registro.item
    
    types = Type.objects.all()
    locations = Location.objects.all()
    marcas = Marca.objects.all()
    items = Item.objects.all()
    
    if request.method == 'POST':
        registro.cod_barras = request.POST.get('cod_barras')
        registro.no_referencia_inv = request.POST.get('no_referencia_inv')
        
        fecha_caducidad = request.POST.get('fecha_caducidad')
        if fecha_caducidad:
            registro.fecha_caducidad = fecha_caducidad
            
        fecha_recepcion = request.POST.get('fecha_recepcion')
        if (fecha_recepcion):
            registro.fecha_recepcion = fecha_recepcion
            
        registro.lote = request.POST.get('lote')
        nueva_cantidad = int(request.POST.get('cantidad'))
        diferencia_cantidad = nueva_cantidad - registro.cantidad
        
        registro.cantidad = nueva_cantidad
        registro.cod = request.POST.get('cod')
        registro.status = request.POST.get('status')
        registro.precio = request.POST.get('precio')
        
        # Actualizar marca, equipo y nivel
        marca_id = request.POST.get('marca')
        ubicacion_id = request.POST.get('ubicacion')
        nivel = request.POST.get('nivel')
        
        if marca_id:
            registro.marca = get_object_or_404(Marca, pk=marca_id)
        
        if ubicacion_id:
            registro.equipo = get_object_or_404(Location, pk=ubicacion_id)
        
        if nivel:
            registro.nivel = nivel
        
        registro.save()
        
        item.stock += diferencia_cantidad
        item.save()
        messages.success(request, 'Se modificó correctamente el registro')
        return redirect('/inventario/')  
    
    return render(request, 'editar_registro.html', {
        'registro': registro,
        'item': item,
        'types': types,
        'locations': locations,
        'marcas': marcas,
        'items': items
    })

from decimal import Decimal
@permission_required('app.add_registro')
@login_required
def registrar_item(request):
    items = Item.objects.all()

    if request.method == 'POST':
        item_id = int(request.POST.get('item'))
        item = get_object_or_404(Item, pk=item_id)

        cod_barras = request.POST.get('cod_barras')
        no_referencia_inv = request.POST.get('no_referencia_inv')
        fecha_caducidad = request.POST.get('fecha_caducidad')
        lote = request.POST.get('lote')
        fecha_recepcion = request.POST.get('fecha_recepcion')
        cantidad = int(request.POST.get('cantidad'))
        cod = request.POST.get('cod')
        status = request.POST.get('status')
        
        # Obtener el precio y convertirlo a float
        precio_str = request.POST.get('precio')
        precio = Decimal(precio_str.replace(',', '.')) if precio_str else None

        # Crear el registro y automáticamente ajustar el stock del item
        registro = Registro(
            item=item,
            cod_barras=cod_barras,
            no_referencia_inv=no_referencia_inv,
            fecha_caducidad=fecha_caducidad,
            lote=lote,
            fecha_recepcion=fecha_recepcion,
            cantidad=cantidad,
            cod=cod,
            status=status,
            precio=precio,
            usuario=request.user
        )
        registro.save()

        return redirect('/inventario/')

    return render(request, 'item_r.html', {
        'items': items
    })


@permission_required('app.delete_registro')
@login_required
def eliminar_registro(request, registro_id):
    if request.method == 'POST':
        try:
            registro = get_object_or_404(Registro, pk=registro_id) 
            registro.usuario = request.user 
            registro.delete()
            return redirect('inventario')  
        except Registro.DoesNotExist:
            pass
    return redirect('inventario')


def registro(request):
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            user = formulario.save(commit=False)  # Crear la instancia del usuario pero no guardar aún
            user.is_active = False  # Desactivar el usuario
            user.save()  # Guardar el usuario con is_active=False

            username = formulario.cleaned_data['username']
            password = formulario.cleaned_data['password1']
            # No es necesario autenticar aquí porque el usuario no está activo
            messages.success(request, "Te has registrado correctamente, pero tu cuenta necesita ser activada por un administrador.")
            return redirect('login')
        else:
            messages.error(request, "El formulario de registro no es válido")
    else:
        formulario = CustomUserCreationForm()

    return render(request, 'registration/registro.html', {'form': formulario})



User = get_user_model()
def recuperar_contraseña(request):
    contraseña_desencriptada = None
    mensaje = None
    opciones_pregunta_recuperacion = User.PREGUNTA_RECUPERACION_CHOICES

    if request.method == 'POST':
        email = request.POST.get('email')
        pregunta = request.POST.get('pregunta_recuperacion')
        respuesta = request.POST.get('respuesta_recuperacion')

        try:
            user = User.objects.get(email=email, pregunta_recuperacion=pregunta)

            if respuesta == user.respuesta_recuperacion:
                contraseña_desencriptada = user.plaintext_password

                if not contraseña_desencriptada:
                    mensaje = "No se puede mostrar la contraseña porque está vacía o no está establecida."
                else:
                    mensaje = f"La contraseña de {user.email} es: {contraseña_desencriptada}"
            else:
                mensaje = "La respuesta de recuperación no es correcta."
        except User.DoesNotExist:
            mensaje = "No se encontró ningún usuario con ese correo."

    return render(request, 'recuperar_contraseña.html', {'mensaje': mensaje, 'opciones_pregunta_recuperacion': opciones_pregunta_recuperacion})

def acerca(request):
            return render(request, 'acerca.html')

def salir(request):
    logout(request)
    return redirect('/')




@login_required
def crear_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.usuario = request.user  # Asignar el usuario actual
            item.save()
            form.save_m2m()  # Guardar las relaciones ManyToMany después de guardar el item

            messages.success(request, 'El item se ha creado correctamente.')
            return redirect('listar_items')
    else:
        form = ItemForm()

    context = {
        'form': form,
        'types': Type.objects.all(),
        'locations': Location.objects.all(),
        'marcas': Marca.objects.all(),
        'proveedores': Proveedor.objects.all(),
    }
    return render(request, 'crear_item.html', context)



@permission_required('app.change_item')
@login_required
def editar_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    types = Type.objects.all()
    locations = Location.objects.all()
    marcas = Marca.objects.all()
    proveedores = Proveedor.objects.all()

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            item.usuario = request.user
            item.save()

            descripcion_personalizada = request.POST.get('descripcion_personalizada', '')
            if not descripcion_personalizada:
                messages.warning(request, 'No se proporcionó ninguna descripción personalizada.')
                Bitacora.objects.create(
                    accion='Actualizar',
                    usuario=request.user,
                    modelo='Item',
                    instancia_id=item.id,
                    descripcion=''
                )
            else:
                Bitacora.objects.create(
                    accion='Actualizar',
                    usuario=request.user,
                    modelo='Item',
                    instancia_id=item.id,
                    descripcion=descripcion_personalizada
                )
                messages.success(request, 'Se modificó correctamente el item con la descripción personalizada.')

            return redirect('listar_items')
    else:
        form = ItemForm(instance=item)

    return render(request, 'editar_item.html', {
        'form': form,
        'item': item,
        'types': types,
        'locations': locations,
        'marcas': marcas,
        'proveedores': proveedores
    })



def listar_items(request):
    items = Item.objects.all()
    return render(request, 'listar_items.html', {'items': items})


@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if request.method == 'POST':
        usuario = request.user
        descripcion_personalizada = request.POST.get('descripcion_personalizada', '')

        # Actualizar el stock del Item
        for registro in item.registro_set.all():
            item.stock -= registro.cantidad
        item.save()

        # Llama a delete y pasa los argumentos adicionales
        item.delete(usuario=usuario, descripcion_personalizada=descripcion_personalizada)

        return redirect('listar_items')
    return render(request, 'eliminar_item.html', {'item': item})


@permission_required('app.view_receta')
@login_required
def recetas(request):
    recetas = Receta.objects.all()
    recetas_items = RecetaItem.objects.all()
    recetas_recetas = RecetaReceta.objects.all()
    context = {
        'recetas': recetas,
        'recetas_items': recetas_items,
        'recetas_recetas': recetas_recetas
    }
    
    return render(request, 'recetas.html', context)




@permission_required('app.add_receta')
@login_required
def Recetas_registrar(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        ingredientes = request.POST.getlist('ingredientes')
        cantidades = request.POST.getlist('cantidades')
        subrecetas = request.POST.getlist('subrecetas')
        subcantidades = request.POST.getlist('subcantidades')

        receta = Receta(nombre=nombre, descripcion=descripcion)
        receta.save()

        for i in range(len(ingredientes)):
            try:
                registro = Registro.objects.get(pk=ingredientes[i])
                item = registro.item
                cantidad = int(cantidades[i])
                RecetaItem.objects.create(receta=receta, item=item, cantidad=cantidad, registro=registro)
            except Registro.DoesNotExist:
                messages.error(request, f'Error: El Registro con ID {ingredientes[i]} no existe.')

        for i in range(len(subrecetas)):
            if subrecetas[i] and subcantidades[i]:  # Verifica que subrecetas[i] y subcantidades[i] no estén vacíos
                try:
                    subreceta = Receta.objects.get(pk=subrecetas[i])
                    cantidad = int(subcantidades[i])
                    RecetaReceta.objects.create(receta=receta, subreceta=subreceta, cantidad=cantidad)
                except Receta.DoesNotExist:
                    messages.error(request, f'Error: La Subreceta con ID {subrecetas[i]} no existe.')

        messages.success(request, 'Receta registrada exitosamente')
        return redirect('/recetas/')  # Redirige a la vista de recetas después de registrar

    registros = Registro.objects.all()  # Obtén todos los registros disponibles
    recetas = Receta.objects.all()

    context = {
        'registros': registros,
        'recetas': recetas
    }

    return render(request, 'registrar_receta.html', context)





permission_required('app.change_Recetas')  
@login_required
def Recetas_editar(request):
    return render(request, 'editar_receta.html') 

from django.http import JsonResponse

@permission_required('app.view_receta')
@login_required
@require_POST
def cotizar_receta(request, receta_id):
    try:
        data = json.loads(request.body)
        cantidad = int(data.get('cantidad', 1))  # Convertir la cantidad a entero

        receta = Receta.objects.get(id=receta_id)
        total_costo = 0

        # Calcular costo de los ingredientes
        ingredientes = []
        for receta_item in receta.recetaitem_set.all():
            total_costo += receta_item.registro.precio * receta_item.cantidad * cantidad
            ingredientes.append(f"{receta_item.cantidad} de {receta_item.item.nombre}")

        # Calcular costo de las subrecetas
        subrecetas = []
        for receta_receta in receta.receta_principal.all():
            subreceta_costo = 0
            subreceta = receta_receta.subreceta
            for subreceta_item in subreceta.recetaitem_set.all():
                subreceta_costo += subreceta_item.registro.precio * subreceta_item.cantidad * cantidad
            total_costo += subreceta_costo * receta_receta.cantidad
            subrecetas.append(f"{receta_receta.cantidad} de {subreceta.nombre}")

        data = {
            "success": True,
            "total_costo": float(total_costo),
            "ingredientes": ingredientes,
            "subrecetas": subrecetas
        }
    except Receta.DoesNotExist:
        data = {"success": False, "error": "Receta no encontrada"}
    except Exception as e:
        data = {"success": False, "error": str(e)}
    return JsonResponse(data)

import json


@permission_required('app.add_receta')
@require_POST
@login_required
def usar_receta(request):
    try:
        data = json.loads(request.body)
        receta_id = data.get('recetaId')
        cantidad = int(data.get('cantidad', 1))  # Convertir la cantidad a entero

        if not receta_id:
            return JsonResponse({'error': 'No se proporcionó una receta válida'}, status=400)

        receta = Receta.objects.get(id=receta_id)

        # Inicia una transacción para garantizar la integridad de los datos
        with transaction.atomic():
            # Calcular costo total de la receta
            total_costo = 0

            # Descontar los ingredientes de la receta
            for receta_item in receta.recetaitem_set.all():
                item = receta_item.item
                cantidad_requerida = receta_item.cantidad * cantidad
                registro = receta_item.registro

                if registro.cantidad >= int(cantidad_requerida):  # Convertir cantidad_requerida a entero
                    registro.cantidad -= cantidad_requerida
                    registro.save()
                else:
                    return JsonResponse({'error': f'No hay suficiente stock en el registro ID {registro.id} para {item.nombre}'}, status=400)

                if item.stock >= cantidad_requerida:  # Comparar con cantidad_requerida (ya un entero)
                    item.stock -= cantidad_requerida
                    item.save()
                else:
                    return JsonResponse({'error': f'No hay suficiente stock de {item.nombre}'}, status=400)

                total_costo += receta_item.registro.precio * receta_item.cantidad * cantidad

            # Descontar las subrecetas de la receta
            for receta_receta in receta.receta_principal.all():
                subreceta = receta_receta.subreceta
                cantidad_requerida = receta_receta.cantidad * cantidad

                # Descontar los ingredientes de la subreceta
                for subreceta_item in subreceta.recetaitem_set.all():
                    item = subreceta_item.item
                    cantidad_subrequerida = subreceta_item.cantidad * cantidad_requerida
                    registro = subreceta_item.registro

                    if registro.cantidad >= int(cantidad_subrequerida):  # Convertir cantidad_subrequerida a entero
                        registro.cantidad -= cantidad_subrequerida
                        registro.save()
                    else:
                        return JsonResponse({'error': f'No hay suficiente stock en el registro ID {registro.id} para {item.nombre}'}, status=400)

                    if item.stock >= cantidad_subrequerida:  # Comparar con cantidad_subrequerida (ya un entero)
                        item.stock -= cantidad_subrequerida
                        item.save()
                    else:
                        return JsonResponse({'error': f'No hay suficiente stock de {item.nombre}'}, status=400)

                    total_costo += subreceta_item.registro.precio * subreceta_item.cantidad * cantidad_subrequerida

            # Guardar el registro de uso de receta
            uso_receta = UsoReceta.objects.create(
                receta=receta,
                cantidad=cantidad,
                cotizacion_total=total_costo,
                usuario=request.user
            )

        return JsonResponse({'success': True})
    except Receta.DoesNotExist:
        return JsonResponse({'error': 'La receta especificada no existe'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


    
    
    
@permission_required('app.delete_receta')
@login_required
def eliminar_receta(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id)
    if request.method == 'POST':
        usuario = request.user

        # Eliminar la receta
        receta.delete()

        return JsonResponse({'message': 'Receta eliminada exitosamente', 'usuario': usuario.username})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    
def resumen_receta(request, receta_id):
    try:
        receta = Receta.objects.get(id=receta_id)
        ingredientes = [
            {
                "nombre": ri.item.nombre,
                "registroId": ri.registro.id,
                "cantidad": ri.cantidad
            }
            for ri in receta.recetaitem_set.all()
        ]
        subrecetas = [
            {
                "nombre": rr.subreceta.nombre,
                "cantidad": rr.cantidad
            }
            for rr in receta.receta_principal.all()
        ]
        data = {
            "success": True,
            "receta": {
                "id": receta.id,
                "nombre": receta.nombre,
                "descripcion": receta.descripcion,
                "ingredientes": ingredientes,
                "subrecetas": subrecetas
            }
        }
    except Receta.DoesNotExist:
        data = {"success": False, "error": "Receta no encontrada"}
    return JsonResponse(data)


permission_required('app.view_type')
@login_required
def type(request):
    types = Type.objects.all()
    return render(request, 'type.html', {'types': types})

@login_required
@permission_required('app.delete_type', raise_exception=True)
def eliminar_type(request, id):
    if request.method == 'POST':
        type_obj = get_object_or_404(Type, id=id)
        type_obj.usuario = request.user
        type_obj.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
@permission_required('app.add_type', raise_exception=True)
def crear_type(request):
    if request.method == 'POST':
        form = TypeForm(request.POST)
        if form.is_valid():
            type_obj = form.save(commit=False)
            type_obj.usuario = request.user
            type_obj.save()
            return redirect('type')
    else:
        form = TypeForm()
    return render(request, 'crear_type.html', {'form': form})



@login_required
@permission_required('app.change_type', raise_exception=True)
def editar_type(request, id):
    type_obj = get_object_or_404(Type, id=id)
    if request.method == 'POST':
        form = TypeForm(request.POST, instance=type_obj)
        if form.is_valid():
            form.save()
            return redirect('type')
    else:
        form = TypeForm(instance=type_obj)
    return render(request, 'editar_type.html', {'form': form})




@login_required
@permission_required('app.view_location', raise_exception=True)
def listar_locations(request):
    locations = Location.objects.all()
    return render(request, 'locations.html', {'locations': locations})



@login_required
@permission_required('app.add_location', raise_exception=True)
def crear_location(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.usuario = request.user
            location.save()
            messages.success(request, 'Se agregó la ubicación correctamente')
            return redirect('listar_locations')
    else:
        form = LocationForm()
    return render(request, 'crear_locations.html', {'form': form})


@permission_required('app.change_location')
@login_required
def editar_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            location = form.save(commit=False)
            location.usuario = request.user
            location.save()

            descripcion_personalizada = request.POST.get('descripcion_personalizada', '')
            if not descripcion_personalizada:
                messages.warning(request, 'No se proporcionó ninguna descripción personalizada.')
                Bitacora.objects.create(
                    accion='Actualizar',
                    usuario=request.user,
                    modelo='Location',
                    instancia_id=location.id,
                    descripcion=f''
                )
            else:
                Bitacora.objects.create(
                    accion='Actualizar',
                    usuario=request.user,
                    modelo='Location',
                    instancia_id=location.id,
                    descripcion=descripcion_personalizada
                )
                messages.success(request, 'Se modificó correctamente la ubicación con la descripción personalizada.')

            return redirect('listar_locations')
    else:
        form = LocationForm(instance=location)
    return render(request, 'editar_locations.html', {'form': form, 'location': location})

@login_required
@permission_required('app.delete_location', raise_exception=True)
def eliminar_location(request, location_id):
    location = get_object_or_404(Location, id=location_id)
    if request.method == 'POST':
        usuario = request.user
        descripcion_personalizada = request.POST.get('descripcion_personalizada', '')


        Bitacora.objects.create(
            accion='Eliminar',
            usuario=usuario,
            modelo='Location',
            instancia_id=location.id,
            descripcion=descripcion_personalizada
        )

        location.delete()

        return redirect('listar_locations')
    return render(request, 'eliminar_location.html', {'location': location})



@login_required
def lista_usos_receta(request):
    usos_recetas = UsoReceta.objects.all().order_by('-fecha_uso')
    context = {
        'usos_recetas': usos_recetas
    }
    return render(request, 'lista_usos_receta.html', context)

import datetime
@login_required
def generar_reporte(request):
    if request.method == 'POST':
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            fecha_inicio = timezone.datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = timezone.datetime.strptime(fecha_fin, '%Y-%m-%d').date()

            usos_recetas = UsoReceta.objects.filter(fecha_uso__date__range=(fecha_inicio, fecha_fin)).order_by('-fecha_uso')

            # Crear el PDF
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)

            # Título del reporte
            p.drawString(1 * inch, 10 * inch, f"Reporte de Usos de Recetas del {fecha_inicio} al {fecha_fin}")

            # Table headers
            p.drawString(0.5 * inch, 9.5 * inch, "Receta")
            p.drawString(2 * inch, 9.5 * inch, "Cantidad")
            p.drawString(3 * inch, 9.5 * inch, "Cotización Total")
            p.drawString(5 * inch, 9.5 * inch, "Fecha de Uso")

            y = 9.25 * inch
            total_cantidad = 0
            total_costo = 0

            for uso in usos_recetas:
                p.drawString(0.5 * inch, y, uso.receta.nombre)
                p.drawString(2 * inch, y, str(uso.cantidad))
                p.drawString(3 * inch, y, f"${uso.cotizacion_total:.2f}")
                p.drawString(5 * inch, y, uso.fecha_uso.strftime('%d %b %Y %H:%M'))

                total_cantidad += uso.cantidad
                total_costo += uso.cotizacion_total

                y -= 0.25 * inch

            # Totales
            p.drawString(1 * inch, y, f"Total Cantidad: {total_cantidad}")
            p.drawString(3 * inch, y, f"Total Costo: ${total_costo:.2f}")

            p.showPage()
            p.save()

            buffer.seek(0)
            filename = f"reporte_usos_recetas_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.write(buffer.getvalue())

            return response

    return render(request, 'generar_reporte.html')

