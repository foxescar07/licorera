from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .forms import ProveedorForm
from .models import Proveedor, Compra 
from .formscomp import CompraForm
# ===============================
# VISTA PARA CREAR NUEVO PROVEEDOR
# ===============================
def nuevo_proveedor(request):
    if request.method == "POST":
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save(commit=False)
            if request.user.is_authenticated:
                proveedor.registrado_por = request.user
            proveedor.save()
            messages.success(request, f"Nuevo proveedor '{proveedor.nombre_empresa}' registrado ✅")
            return redirect('proveedores')
        else:
            messages.error(request, "Error: El proveedor ya existe o los datos no son válidos")
    else:
        form = ProveedorForm()
    return render(request, "proveedores/proveedor.html", {"form": form})

# ===============================
# VISTA PRINCIPAL: DASHBOARD DE PROVEEDORES
# ===============================
def inicio_proveedores(request):
    proveedores = Proveedor.objects.all().order_by('-ultima_modificacion')

    # Estadísticas para tarjetas
    total = proveedores.count()
    hace_30_dias = timezone.now() - timedelta(days=30)
    nuevos = proveedores.filter(fecha_registro__gte=hace_30_dias).count()
    ultimo = proveedores.order_by('-ultima_modificacion').first()
    fecha_u = ultimo.ultima_modificacion if ultimo else None

    # Logica para guardar nuevo proveedor desde modal
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            if request.user.is_authenticated:
                p.registrado_por = request.user
                p.modificado_por = request.user
            p.save()
            messages.success(request, f'¡Proveedor "{p.nombre_empresa}" registrado!')
            return redirect('proveedores') 
    else:
        form = ProveedorForm()

    context = {
        'proveedores': proveedores,
        'form': form,
        'total_proveedores': total,
        'nuevos_mes': nuevos,
        'proveedores_activos': total,
        'porcentaje_activos': 100 if total > 0 else 0,
        'ultima_actualizacion': fecha_u,
    }
    return render(request, 'proveedores/proveedor.html', context)

# ===============================
# VISTA PARA EDITAR PROVEEDOR
# ===============================
def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            p = form.save(commit=False)
            if request.user.is_authenticated:
                p.modificado_por = request.user
            p.ultima_modificacion = timezone.now()
            p.save()
            messages.success(request, f'¡Proveedor "{p.nombre_empresa}" actualizado correctamente! ✅')
            return redirect('proveedores')
        else:
            messages.error(request, "Error al actualizar proveedor")
    else:
        form = ProveedorForm(instance=proveedor)

    return render(request, 'proveedores/editar_proveedor.html', {
        'form': form,
        'proveedor': proveedor
    })

# ===============================
# VISTA PARA ELIMINAR PROVEEDOR
# ===============================
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        nombre = proveedor.nombre_empresa
        proveedor.delete()
        messages.warning(request, f'Proveedor "{nombre}" eliminado correctamente 🗑️')
    return redirect('proveedores')
def registrar_compra(request, proveedor_id):
    proveedor = get_object_or_404(Proveedor, id=proveedor_id)
    if request.method == 'POST':
        form = CompraForm(request.POST)
        if form.is_valid():
            compra = form.save(commit=False)
            compra.proveedor = proveedor  # asigna la compra al proveedor
            if request.user.is_authenticated:
                compra.registrado_por = request.user
            compra.save()
            messages.success(request, f"Compra de '{compra.producto}' registrada ✅")
            return redirect('proveedores')  # o redirige donde quieras
    else:
        form = CompraForm()

    compras = Compra.objects.filter(proveedor=proveedor).order_by('-fecha_registro')

    return render(request, 'proveedores/compra.html', {
        'form': form,
        'compras': compras,
        'proveedor': proveedor
    })