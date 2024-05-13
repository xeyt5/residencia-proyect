from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout, authenticate, login
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Item, Registro, Location, Type, Marca, Proveedor
from .forms import RegistroForm, marcaform, proveedorForm
from django.http import JsonResponse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType

# Create your views here.

@permission_required('app.view_auth_permission')
@login_required
def asignar_permisos(request):
    usuarios = User.objects.all()
    
    # Filtrar los content types relacionados con tus modelos
    content_types = ContentType.objects.filter(
        app_label='app', 
        model__in=['location', 'marca', 'proveedor', 'item']
    )
    
    # Obtener los permisos relacionados con los content types filtrados
    permisos = Permission.objects.filter(content_type__in=content_types)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        selected_user = User.objects.get(username=username)
        permission_ids = request.POST.getlist('permissions')
        
        # Primero, eliminamos todos los permisos actuales del usuario
        selected_user.user_permissions.clear()
        
        # Luego, asignamos los nuevos permisos seleccionados
        for permission_id in permission_ids:
            permission = Permission.objects.get(id=permission_id)
            selected_user.user_permissions.add(permission)
        
        return redirect('asignar_permisos')
    
    selected_username = request.GET.get('username')
    selected_user = User.objects.filter(username=selected_username).first()
    selected_user_permissions = selected_user.user_permissions.all() if selected_user else []
    
    return render(request, 'asignar_permisos.html', {
        'usuarios': usuarios,
        'permisos': permisos,
        'selected_username': selected_username,
        'selected_user_permissions': selected_user_permissions
    })



@login_required
def index(request):
        return render(request, 'index.html')
   
 
@login_required
def marca(request):
    Marcas = Marca.objects.all()
    return render(request, 'marca.html', {'Marcas':Marcas})
  
@login_required
def eliminar_marca(request, marca_id):
    marca = get_object_or_404(Marca, id=marca_id)
    if request.method == 'POST':
        marca.delete()
        return JsonResponse({'message': 'Marca eliminada exitosamente'})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405) 
    
@login_required
def marcaregistro(request):
    if request.method == 'POST':
        form = marcaform(request.POST)
        if form.is_valid():
            form.save()
            return redirect('marca') 
    else:
        form = marcaform()
    return render(request, 'insertar_marca.html', {'form': form})


@login_required
def editar_marca(request, marca_id):
    marca = get_object_or_404(Marca, id=marca_id)
    if request.method == 'POST':
        form = marcaform(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            return redirect('marca')  
    else:
        form = marcaform(instance=marca)
    return render(request, 'editar_marca.html', {'form': form})
    
    
@login_required
def provedores(request):
    Proveedores = Proveedor.objects.all()
    return render(request, 'proveedores.html', {'Proveedores':Proveedores})  

@login_required
def eliminar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        proveedor.delete()
        return JsonResponse({'message': 'Proveedor eliminado exitosamente'})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

permission_required('app.add_Proveedor')
@login_required
def proveedoresregistro(request):
        if request.method == 'POST':
         form = proveedorForm(request.POST)
         if form.is_valid():
                form.save()
                return redirect('/proveedores/')
        else:
                form = proveedorForm()
        return render(request, 'proveedoresr.html', {'form': form})
    
@login_required
def editar_proveedor(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        form = proveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
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

@permission_required('app.view_item')
@login_required    
def inventario(request):
    items = Item.objects.all()
    registros = Registro.objects.all() 
    types = Type.objects.all()
    locations = Location.objects.all()
    Marcas = Marca.objects.all()
    
    return render(request, 'inventario.html', {'items': items, 'registros': registros, 'types': types, 'locations': locations, 'Marcas':Marcas})

@permission_required('app.change_item')
@login_required
def editar_item(request, registro_id):
    registro = get_object_or_404(Registro, pk=registro_id)
    item = registro.item
    
    # Obtener todas las instancias de Type, Location y Marca
    types = Type.objects.all()
    locations = Location.objects.all()
    marcas = Marca.objects.all()
    
    # Si el método de la solicitud es POST, significa que se envió el formulario de edición
    if request.method == 'POST':
        # Actualiza el ítem con los datos del formulario
        item.nombre = request.POST.get('nombre')
        item.contenido = request.POST.get('contenido')
        item.unidad_de_medida = request.POST.get('unidad_medida')
        item.stock = request.POST.get('stock')
        
        # Actualiza las relaciones ManyToMany con los nuevos valores seleccionados
        tipos_seleccionados = request.POST.getlist('tipo')
        item.types.set(tipos_seleccionados)
        
        ubicaciones_seleccionadas = request.POST.getlist('ubicacion')
        item.locations.clear()
        for ubicacion_id in ubicaciones_seleccionadas:
            ubicacion = Location.objects.get(pk=ubicacion_id)
            item.locations.add(ubicacion)
        
        # Actualiza la marca del ítem
        marca_id = request.POST.get('marca')
        marca = Marca.objects.get(pk=marca_id)
        item.marcas.clear()  # Limpiamos las marcas existentes
        item.marcas.add(marca)  # Agregamos la nueva marca
        
        # Actualiza los campos del registro relacionado
        registro.cod_barras = request.POST.get('cod_barras')
        registro.no_referencia_inv = request.POST.get('no_referencia_inv')
        
        fecha_caducidad = request.POST.get('fecha_caducidad')
        if fecha_caducidad:
            registro.fecha_caducidad = fecha_caducidad
            
        fecha_recepcion = request.POST.get('fecha_recepcion')
        if fecha_recepcion:
            registro.fecha_recepcion = fecha_recepcion
            
        registro.lote = request.POST.get('lote')
        registro.cantidad = request.POST.get('cantidad')
        registro.cod = request.POST.get('cod')
        registro.status = request.POST.get('status')
        registro.save()
        
        item.save()
        return redirect('/inventario/')  # Ajusta el nombre de la URL según tu configuración
    
    return render(request, 'editar_item.html', {'item': item, 'types': types, 'locations': locations, 'marcas': marcas, 'registro': registro})



@login_required
def registrar_item(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/inventario/')
    else:
        form = RegistroForm()
    return render(request, 'item_r.html', {'form': form})

permission_required('app.delete_item')
@login_required
def eliminar_item(request, item_id):
    if request.method == 'POST':
        try:
            item = Item.objects.get(pk=item_id)
            item.delete()
            return redirect('inventario')  # Redirecciona a la página de inventario después de eliminar el ítem
        except Item.DoesNotExist:
            pass
    return redirect('inventario')  # Redirecciona a la página de inventario



def registro(request):
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            user = formulario.save()
            username = formulario.cleaned_data['username']
            password = formulario.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                messages.success(request, "Te has registrado correctamente")
                return redirect('login') 
            else:
                messages.error(request, "No se pudo iniciar sesión automáticamente después del registro")
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

