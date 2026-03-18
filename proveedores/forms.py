

from proveedores.models import Proveedor
from django.forms import ModelForm

class ProveedorForm(ModelForm):
    
    class Meta:
        model = Proveedor
        fields = "__all__"
