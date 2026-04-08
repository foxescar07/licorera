from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Proveedor
from .forms import ProveedorForm

# VISTA PRINCIPAL: Lista y Crea proveedores
def inicio_proveedores(request):
    proveedores = Proveedor.objects.all().order_by('-ultima_modificacion')

    # Cálculos para las tarjetas de estadísticas
    total = proveedores.count()
    hace_30_dias = timezone.now() - timedelta(days=30)
    nuevos = proveedores.filter(fecha_registro__gte=hace_30_dias).count()
    
    ultimo = proveedores.order_by('-ultima_modificacion').first()
    fecha_u = ultimo.ultima_modificacion if ultimo else None

    # Lógica para guardar un nuevo proveedor (Modal)
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            # Guardamos quién lo creó si está logueado
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

# VISTA PARA EDITAR: Sincronizada con el Front
def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == 'POST':
        # VITAL: instance=proveedor vincula el formulario al registro existente en la BD
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            p = form.save(commit=False)
            # Mantenemos tu lógica de usuario responsable
            if request.user.is_authenticated:
                p.modificado_por = request.user
            
            # Forzamos la actualización de la fecha para que aparezca en el front
            p.ultima_modificacion = timezone.now()
            p.save() # Aquí se guardan los cambios físicos en la base de datos
            
            messages.success(request, f'¡"{p.nombre_empresa}" actualizado correctamente!')
            return redirect('proveedores')
    else:
        # Cargamos el formulario con los datos actuales del proveedor
        form = ProveedorForm(instance=proveedor)

    return render(request, 'proveedores/editar_proveedor.html', {
        'form': form,
        'proveedor': proveedor
    })

# VISTA PARA ELIMINAR
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        nombre = proveedor.nombre_empresa
        proveedor.delete()
        messages.warning(request, f'El proveedor "{nombre}" ha sido eliminado.')
    return redirect('proveedores')