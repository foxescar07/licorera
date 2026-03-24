from django.shortcuts import render, redirect, get_object_or_404
from .models import Proveedor
from .forms import ProveedorForm
from django.contrib.auth.models import User

def inicio_proveedores(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save(commit=False)
            user = User.objects.first()
            if user:
                proveedor.registrado_por = user
                proveedor.save()
                return redirect('proveedores')
    else:
        form = ProveedorForm()
    
    proveedores = Proveedor.objects.all()
    return render(request, 'proveedores/proveedor.html', {'form': form, 'proveedores': proveedores})

def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            return redirect('proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    
    proveedores = Proveedor.objects.all()
    return render(request, 'proveedores/proveedor.html', {
        'form': form,
        'proveedores': proveedores,
        'editando': True,
        'proveedor_id': id
    })

def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    proveedor.delete()
    return redirect('proveedores')