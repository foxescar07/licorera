from django import forms
from .models import Usuario
import hashlib
import re


def validar_clave_segura(clave):
    """Mínimo 6 caracteres, 2 números y 1 mayúscula."""
    if len(clave) < 6:
        raise forms.ValidationError('La contraseña debe tener al menos 6 caracteres.')
    if len(re.findall(r'\d', clave)) < 2:
        raise forms.ValidationError('La contraseña debe contener al menos 2 números.')
    if not re.search(r'[A-Z]', clave):
        raise forms.ValidationError('La contraseña debe contener al menos 1 letra mayúscula.')


class UsuarioForm(forms.ModelForm):
    clave = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control cys-input',
            'placeholder': 'Mín. 6 caracteres, 2 números, 1 mayúscula',
            'id': 'id_clave',
        }),
        label='Contraseña'
    )
    clave_confirmar = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control cys-input',
            'placeholder': 'Confirmar contraseña',
        }),
        label='Confirmar Contraseña'
    )

    class Meta:
        model  = Usuario
        fields = ['tipo_id', 'identificacion', 'nombre', 'apellidos',
                  'email', 'usuario', 'rol']
        widgets = {
            'tipo_id':        forms.Select(attrs={'class': 'form-select cys-input'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control cys-input', 'placeholder': 'Número de identificación'}),
            'nombre':         forms.TextInput(attrs={'class': 'form-control cys-input', 'placeholder': 'Nombres'}),
            'apellidos':      forms.TextInput(attrs={'class': 'form-control cys-input', 'placeholder': 'Apellidos'}),
            'email':          forms.EmailInput(attrs={'class': 'form-control cys-input', 'placeholder': 'correo@ejemplo.com'}),
            'usuario':        forms.TextInput(attrs={'class': 'form-control cys-input', 'placeholder': 'Nombre de usuario'}),
            'rol':            forms.Select(attrs={'class': 'form-select cys-input'}),
        }

    def clean_identificacion(self):
        v = self.cleaned_data.get('identificacion', '')
        if not v.isdigit():
            raise forms.ValidationError('Solo debe contener números.')
        qs = Usuario.objects.filter(identificacion=v)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un usuario con esta identificación.')
        return v

    def clean_usuario(self):
        v = self.cleaned_data.get('usuario', '')
        qs = Usuario.objects.filter(usuario=v)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return v

    def clean_nombre(self):
        v = self.cleaned_data.get('nombre', '')
        if any(c.isdigit() for c in v):
            raise forms.ValidationError('El nombre no debe contener números.')
        return v

    def clean_apellidos(self):
        v = self.cleaned_data.get('apellidos', '')
        if any(c.isdigit() for c in v):
            raise forms.ValidationError('Los apellidos no deben contener números.')
        return v

    def clean_clave(self):
        clave = self.cleaned_data.get('clave', '')
        validar_clave_segura(clave)
        return clave

    def clean(self):
        cleaned = super().clean()
        c1 = cleaned.get('clave')
        c2 = cleaned.get('clave_confirmar')
        if c1 and c2 and c1 != c2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned

    def save(self, commit=True):
        u = super().save(commit=False)
        u.clave = hashlib.sha256(self.cleaned_data['clave'].encode()).hexdigest()
        if commit:
            u.save()
        return u