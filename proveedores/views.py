from django.shortcuts import render

from proveedores.forms import ProveedorForm

# Create your views here.
def inicio_proveedores(request):
    form= ProveedorForm()
    print("Hola")
    context={
        'form': form,
    }
    print(form)
    return render(request, 'proveedor.html',context)