from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from user.models import User
from django.core.exceptions import ValidationError
from django import forms
from .models import Item, Registro, Type, Location, Marca, Proveedor

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)
    respuesta_recuperacion = forms.CharField(max_length=400, label='Respuesta de recuperación')

    def clean_username(self):
        username = self.cleaned_data['username']
        # Verificar si hay más de 2 veces la misma letra en el nombre de usuario
        for i in range(len(username) - 2):
            if username[i] == username[i+1] == username[i+2]:
                raise ValidationError("No se pueden ingresar más de 2 veces la misma letra en el nombre de usuario")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'pregunta_recuperacion', 'respuesta_recuperacion']

class CustomUserChangeForm(UserChangeForm):
    respuesta_recuperacion = forms.CharField(max_length=400, label='Respuesta de recuperación')

    def clean_username(self):
        username = self.cleaned_data['username']
        # Verificar si hay más de 2 veces la misma letra en el nombre de usuario
        for i in range(len(username) - 2):
            if username[i] == username[i+1] == username[i+2]:
                raise forms.ValidationError("No se pueden ingresar más de 2 veces la misma letra en el nombre de usuario")
        return username

    class Meta:
        model = User
        fields = ['username', 'email', 'pregunta_recuperacion', 'respuesta_recuperacion']



class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        fields = '__all__'
    

class marcaform(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nombre', 'descripcion']
        
        
class proveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre','descripcion','telefono','correo','url']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nombre', 'contenido', 'unidad_de_medida', 'stock','stock_minimo','types', 'locations', 'marcas', 'proveedores']
        
        
class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        fields = ['nombre', 'descripcion']

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['equipo', 'nivel', 'descripcion']
        
