from django.shortcuts import render, redirect, get_object_or_404
from .models import Proveedor
from .forms import ProveedorForm
from django.contrib.auth.models import User
from django.contrib import messages

def inicio_proveedores(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save(commit=False)
            # Intenta usar el usuario logueado, si no, el primero de la BD
            user = request.user if request.user.is_authenticated else User.objects.first()
            proveedor.registrado_por = user
            proveedor.save()
            messages.success(request, "Proveedor guardado con éxito.")
            return redirect('proveedores')
    else:
        form = ProveedorForm()
    
    proveedores = Proveedor.objects.all().order_by('-id')
    return render(request, 'proveedores/proveedor.html', {
        'form': form, 
        'proveedores': proveedores
    })

def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, "Proveedor actualizado.")
            return redirect('proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    
    return render(request, 'proveedores/editar_proveedor.html', {
        'form': form,
        'proveedor': proveedor
    })

def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    proveedor.delete()
    messages.warning(request, "Proveedor eliminado.")
    return redirect('proveedores')