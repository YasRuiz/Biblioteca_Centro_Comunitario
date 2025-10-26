from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Libro, Usuario

# ---------------------------------------------------------
# Formulario de login
# ---------------------------------------------------------
class LoginForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingrese su nombre de usuario'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingrese su contraseña'
        })
    )

# ---------------------------------------------------------
# Formulario para agregar/editar libros
# ---------------------------------------------------------
class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'isbn', 'disponible', 'fecha_publicacion', 'descripcion']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del libro'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Autor del libro'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número ISBN'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_publicacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Descripción del libro...'}),
        }

# ---------------------------------------------------------
# Formulario para crear nuevos usuarios (con rol)
# ---------------------------------------------------------
class CrearUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese el correo electrónico'
        })
    )
    rol = forms.ChoiceField(
        choices=Usuario.ROLES,
        label="Rol del usuario",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol', 'password1', 'password2']
        help_texts = {
            'username': 'Máximo 150 caracteres. Solo letras, números y @/./+/-/_',
            'password1': 'Ingrese una contraseña segura',
            'password2': 'Repita la contraseña para confirmarla',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = self.cleaned_data['rol']
        # Si el rol es bibliotecario, darle is_staff para que aparezca en Django Admin
        user.is_staff = user.rol == 'bibliotecario'
        user.set_password(self.cleaned_data["password1"])  # asegura contraseña segura
        if commit:
            user.save()
        return user

# ---------------------------------------------------------
# Formulario para editar usuarios (Administrador)
# ---------------------------------------------------------
class EditarUsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese nueva contraseña'}),
        required=False
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repita la nueva contraseña'}),
        required=False
    )

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'rol']
        help_texts = {
            'username': 'Máximo 150 caracteres. Solo letras, números y @/./+/-/_',
            'email': 'Correo electrónico válido del usuario',
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        p = self.cleaned_data.get('password1')
        if p:
            user.set_password(p)  # Actualiza contraseña si se ingresó nueva
        # Actualiza is_staff si cambia el rol a bibliotecario
        user.is_staff = user.rol == 'bibliotecario'
        if commit:
            user.save()
        return user
