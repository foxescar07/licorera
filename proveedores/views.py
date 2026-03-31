from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Proveedor
from .forms import ProveedorForm

def inicio_proveedores(request):
    proveedores = Proveedor.objects.all()

    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save(commit=False)
            proveedor.registrado_por = request.user if request.user.is_authenticated else None
            proveedor.modificado_por = request.user if request.user.is_authenticated else None
            proveedor.save()
            messages.success(request, f'¡Proveedor "{proveedor.nombre_empresa}" registrado con éxito!')
            return redirect('proveedores')
    else:
        form = ProveedorForm()

    return render(request, 'proveedores/proveedor.html', {
        'proveedores': proveedores,
        'form': form
    })

def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            p = form.save(commit=False)
            # ✅ Registrar quién editó
            p.modificado_por = request.user if request.user.is_authenticated else None
            p.save()
            messages.success(request, f'¡Proveedor "{proveedor.nombre_empresa}" actualizado correctamente!')
            return redirect('proveedores')
    else:
        form = ProveedorForm(instance=proveedor)

    return render(request, 'proveedores/editar_proveedor.html', {
        'form': form,
        'proveedor_editado': proveedor
    })

def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        nombre = proveedor.nombre_empresa
        proveedor.delete()
        messages.warning(request, f'El proveedor "{nombre}" ha sido eliminado correctamente.')
    return redirect('proveedores')