from django import forms
from .models import Producto, Categoria, AgendaInventario, PresentacionProducto


class ProductoForm(forms.ModelForm):
    class Meta:
        model  = Producto
        fields = ["codigo", "nombre", "descripcion", "categoria"]
        widgets = {
            "nombre":      forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Aguila Lata 330ml"}),
            "codigo":      forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: AGU330"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción opcional..."}),
            "categoria":   forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "nombre":      "Nombre del Producto",
            "codigo":      "Código / Referencia",
            "descripcion": "Descripción (opcional)",
            "categoria":   "Categoría",
        }


class PresentacionForm(forms.ModelForm):
    class Meta:
        model  = PresentacionProducto
        fields = ["nombre", "unidades", "cantidad", "precio"]
        widgets = {
            "nombre":   forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Six-pack"}),
            "unidades": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej: 6", "min": 1}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Stock disponible", "min": 0}),
            "precio":   forms.NumberInput(attrs={"class": "form-control", "placeholder": "Ej: 13000", "min": 0}),
        }
        labels = {
            "nombre":   "Nombre presentación",
            "unidades": "Unidades que contiene",
            "cantidad": "Cantidad existente",  # ✅ Label actualizado
            "precio":   "Precio (COP)",
        }


class AgendaInventarioForm(forms.ModelForm):
    class Meta:
        model  = AgendaInventario
        fields = ["titulo", "descripcion", "fecha_programada", "estado"]
        widgets = {
            "titulo":           forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Conteo mensual licores"}),
            "descripcion":      forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descripción opcional..."}),
            "fecha_programada": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "estado":           forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "titulo":           "Título",
            "descripcion":      "Descripción (opcional)",
            "fecha_programada": "Fecha y Hora",
            "estado":           "Estado",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_programada"].input_formats = ["%Y-%m-%dT%H:%M"]


class ProductoRegistroForm(forms.ModelForm):
    class Meta:
        model  = Producto
        fields = ["codigo", "nombre", "categoria"]
        widgets = {
            "codigo":    forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: AGU330"}),
            "nombre":    forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Aguila Lata"}),
            "categoria": forms.Select(attrs={"class": "form-select"}),
        }