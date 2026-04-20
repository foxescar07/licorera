from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from producto.models import Producto, Inventario
from .models import Proveedor, Compra
from .forms import ProveedorForm


# ===============================
# DASHBOARD PROVEEDORES
# ===============================
def inicio_proveedores(request):
    proveedores = Proveedor.objects.all().order_by('-ultima_modificacion')

    total        = proveedores.count()
    hace_30_dias = timezone.now() - timedelta(days=30)
    nuevos       = proveedores.filter(fecha_registro__gte=hace_30_dias).count()
    ultimo       = proveedores.first()
    fecha_u      = ultimo.ultima_modificacion if ultimo else None

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
        'proveedores':        proveedores,
        'form':               form,
        'total_proveedores':  total,
        'nuevos_mes':         nuevos,
        'proveedores_activos': total,
        'ordenes_pendientes': 0,
        'porcentaje_activos': 100 if total > 0 else 0,
        'ultima_actualizacion': fecha_u,
    }
    return render(request, 'proveedores/proveedor.html', context)


# ===============================
# EDITAR PROVEEDOR
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
            messages.success(request, f'¡Proveedor "{p.nombre_empresa}" actualizado correctamente!')
            return redirect('proveedores')
    else:
        form = ProveedorForm(instance=proveedor)

    return render(request, 'proveedores/editar_proveedor.html', {
        'form': form,
        'proveedor': proveedor
    })


# ===============================
# ELIMINAR PROVEEDOR
# ===============================
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)
    if request.method == 'POST':
        nombre = proveedor.nombre_empresa
        proveedor.delete()
        messages.success(request, f'¡Proveedor "{nombre}" eliminado!')
    return redirect('proveedores')


# ===============================
# REGISTRAR COMPRA
# El ingreso de stock SOLO ocurre aquí.
# Genera 3 registros:
#   1. Compra  →  historial por proveedor
#   2. producto.cantidad_disponible  →  stock actualizado
#   3. Inventario tipo 'entrada'  →  trazabilidad de movimientos
# ===============================
def registrar_compra(request, proveedor_id):
    proveedor_obj = get_object_or_404(Proveedor, id=proveedor_id)
    productos     = Producto.objects.prefetch_related('presentaciones').all()
    compras       = Compra.objects.filter(proveedor=proveedor_obj).order_by('-fecha_registro')

    if request.method == 'POST':
        id_prod = request.POST.get('producto')
        cant    = request.POST.get('cantidad')
        precio  = request.POST.get('precio_unitario')

        if not id_prod or not cant or not precio:
            messages.warning(request, "Completa todos los campos.")
        else:
            try:
                producto_instancia = Producto.objects.get(id=int(id_prod))
                cantidad_int       = int(cant)

                if cantidad_int <= 0:
                    messages.error(request, "La cantidad debe ser mayor a cero.")
                    return redirect('registrar_compra', proveedor_id=proveedor_id)

                # 1. Registro de la compra
                Compra.objects.create(
                    proveedor=proveedor_obj,
                    producto=producto_instancia,
                    cantidad=cantidad_int,
                    precio_unitario=precio
                )

                # 2. Actualizar stock
                producto_instancia.cantidad_disponible += cantidad_int
                producto_instancia.save()

                # 3. Movimiento de inventario para trazabilidad
                Inventario.objects.create(
                    producto=producto_instancia,
                    tipo='entrada',
                    cantidad=cantidad_int,
                    motivo=f'Compra a proveedor: {proveedor_obj.nombre_empresa}',
                    ubicacion='Ingreso por compra'
                )

                messages.success(
                    request,
                    f'✅ {cantidad_int} unidades de "{producto_instancia.nombre}" '
                    f'ingresadas al inventario.'
                )
                return redirect('registrar_compra', proveedor_id=proveedor_id)

            except Producto.DoesNotExist:
                messages.error(request, "El producto seleccionado no existe.")
            except Exception as e:
                messages.error(request, f"Error: {e}")

    return render(request, 'proveedores/compra.html', {
        'proveedor': proveedor_obj,
        'productos': productos,
        'compras':   compras,
    })