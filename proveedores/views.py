from django.shortcuts import render, redirect, get_object_or_404
from .models import Proveedor
from .forms import ProveedorForm

def inicio_proveedores(request):
    proveedores = Proveedor.objects.all()

    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save(commit=False)
            proveedor.registrado_por = request.user if request.user.is_authenticated else None
            proveedor.save()
            return redirect('proveedores')
        else:
            return render(request, 'proveedores/proveedor.html', {
                'proveedores': proveedores,
                'form': form,
                'error_registro': True
            })

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
            p.registrado_por = request.user if request.user.is_authenticated else None
            p.save()
            return redirect('proveedores')
    else:
        form = ProveedorForm(instance=proveedor)

    return render(request, 'proveedores/proveedor.html', {
        'proveedores': Proveedor.objects.all(),
        'form': form,
        'proveedor_editado': proveedor,
        'editando': True
    })

def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        proveedor.delete()
    return redirect('proveedores')