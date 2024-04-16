from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate
from .forms import CustomUserCreationForm

# Create your views here.

@login_required
def index(request):
        return render(request, 'index.html')

@login_required    
def inventario(request):
    return render(request, 'inventario.html')

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


def salir(request):
    logout(request)
    return redirect('/')
