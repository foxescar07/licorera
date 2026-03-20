from django.shortcuts import render, redirect
from .forms import ProveedorForm
from .models import Proveedor
# IMPORTANTE: Cambiamos 'usuario.models' por el oficial de Django
from django.contrib.auth.models import User 

def inicio_proveedores(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            try:
                aux = User.objects.first()  
            except User.DoesNotExist:
                aux = None

            proveedor = form.save(commit=False)
            proveedor.registrado_por = aux
            proveedor.save()

            return redirect('proveedores')
    else:
        form = ProveedorForm()

    proveedores = Proveedor.objects.all()

    context = {
        'form': form,
        'proveedores': proveedores
    }
    return render(request, 'proveedor.html', context)