from django import forms
from .models import Producto, Categoria, AgendaInventario


class ProductoForm(forms.ModelForm):
    """
    Formulario para registrar y editar un Producto.
    Conectado al modal 'modalNuevoProducto' del HTML.
    """

    class Meta:
        model  = Producto
        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "categoria",
            "precio_unitario",
            "cantidad_disponible",
            "unidad",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: Aguila Lata 330ml",
                "id": "nombreProducto",
            }),
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: AGU330",
                "id": "codigo",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ej: Cerveza nacional...",
                "id": "descripcion",
            }),
            "categoria": forms.Select(attrs={
                "class": "form-select",
                "id": "categoria",
            }),
            "unidad": forms.Select(attrs={
                "class": "form-select",
                "id": "unidad",
            }),
            "precio_unitario": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "45000",
                "min": "0",
                "step": "100",
                "id": "precio",
            }),
            "cantidad_disponible": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "50",
                "min": "0",
                "id": "stockInicial",
            }),
        }
        labels = {
            "nombre": "Nombre del Producto",
            "codigo": "Código / Referencia",
            "descripcion": "Descripción (opcional)",
            "categoria": "Categoría",
            "precio_unitario": "Precio Unitario (COP)",
            "cantidad_disponible": "Stock Inicial",
            "unidad": "Unidad",
        }


class AgendaInventarioForm(forms.ModelForm):
    class Meta:
        model  = AgendaInventario
        fields = ["titulo", "descripcion", "fecha_programada", "estado"]
        widgets = {
            "titulo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: Conteo mensual licores",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripción opcional...",
            }),
            "fecha_programada": forms.DateTimeInput(attrs={
                "class": "form-control",
                "type": "datetime-local",
            }, format="%Y-%m-%dT%H:%M"),
            "estado": forms.Select(attrs={
                "class": "form-select",
            }),
        }
        labels = {
            "titulo": "Título",
            "descripcion": "Descripción (opcional)",
            "fecha_programada": "Fecha y Hora",
            "estado": "Estado",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_programada"].input_formats = ["%Y-%m-%dT%H:%M"]


#  NUEVO FORMULARIO 
class ProductoRegistroForm(forms.ModelForm):
    """
    Formulario exclusivo para registrar productos (sin lógica de inventario).
    """

    class Meta:
        model = Producto
        fields = [
            "codigo",
            "nombre",
            "categoria",
            "precio_unitario",
            "unidad",
        ]

        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: AGU330"
            }),
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: Aguila Lata"
            }),
            "categoria": forms.Select(attrs={
                "class": "form-select"
            }),
            "precio_unitario": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0"
            }),
            "unidad": forms.Select(attrs={
                "class": "form-select"
            }),
        }