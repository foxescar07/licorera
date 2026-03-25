from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Venta, Proveedor, Producto
from .forms import VentaForm, ProveedorForm


def reportes(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')

        # ── VENTAS ──────────────────────────────────────────────────────────
        if accion == 'crear_venta':
            form = VentaForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Venta registrada correctamente.')
            else:
                messages.error(request, 'Error al registrar la venta. Revisa los campos.')

        elif accion == 'editar_venta':
            venta_id = request.POST.get('venta_id')
            venta = get_object_or_404(Venta, pk=venta_id)
            form = VentaForm(request.POST, instance=venta)
            if form.is_valid():
                form.save()
                messages.success(request, f'Venta #{venta_id} actualizada.')
            else:
                messages.error(request, 'Error al actualizar la venta. Revisa los campos.')

        elif accion == 'eliminar_venta':
            venta_id = request.POST.get('venta_id')
            venta = get_object_or_404(Venta, pk=venta_id)
            venta.delete()
            messages.success(request, f'Venta #{venta_id} eliminada.')

        # ── PROVEEDORES ──────────────────────────────────────────────────────
        elif accion == 'crear_proveedor':
            form_prov = ProveedorForm(request.POST)
            if form_prov.is_valid():
                form_prov.save()
                messages.success(request, 'Proveedor creado correctamente.')
            else:
                messages.error(request, 'Error al crear el proveedor. Revisa los campos.')

        elif accion == 'editar_proveedor':
            proveedor_id = request.POST.get('proveedor_id')
            proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
            form_prov = ProveedorForm(request.POST, instance=proveedor)
            if form_prov.is_valid():
                form_prov.save()
                messages.success(request, f'Proveedor #{proveedor_id} actualizado.')
            else:
                messages.error(request, 'Error al actualizar el proveedor.')

        elif accion == 'eliminar_proveedor':
            proveedor_id = request.POST.get('proveedor_id')
            proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
            proveedor.delete()
            messages.success(request, f'Proveedor eliminado.')

        # ── REPORTE ──────────────────────────────────────────────────────────
        elif accion == 'generar_reporte':
            # Aquí puedes agregar lógica de exportación PDF/Excel
            messages.info(request, 'Función de reporte en desarrollo.')

        return redirect('reportes')

    # ── GET ──────────────────────────────────────────────────────────────────
    ventas_qs = Venta.objects.select_related('producto__inventario').all()
    proveedores_qs = Proveedor.objects.select_related('producto').all()
    productos = Producto.objects.all()

    # Emparejar cada objeto con su form de edición → iterable en el template
    ventas_con_form = [
        (venta, VentaForm(instance=venta))
        for venta in ventas_qs
    ]
    proveedores_con_form = [
        (proveedor, ProveedorForm(instance=proveedor))
        for proveedor in proveedores_qs
    ]

    # Totales para las tarjetas
    total_ventas = sum(v.total() for v in ventas_qs)

    return render(request, 'reportes.html', {
        'ventas_con_form': ventas_con_form,
        'proveedores_con_form': proveedores_con_form,
        'productos': productos,
        'form': VentaForm(),
        'form_proveedor': ProveedorForm(),
        'total_ventas': total_ventas,
        'total_productos': productos.count(),
        'total_clientes': ventas_qs.values('cliente').distinct().count(),
    })