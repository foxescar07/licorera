from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm
from producto.models import Producto, Inventario, Categoria, PresentacionProducto


def ventas_lista(request):
    ventas     = Venta.objects.prefetch_related('detalles__producto').all()
    form       = VentaForm()
    detalle    = DetalleVentaForm()
    categorias = Categoria.objects.prefetch_related('productos__presentaciones').all()

    return render(request, 'ventas.html', {
        'ventas':     ventas,
        'form':       form,
        'detalle':    detalle,
        'categorias': categorias,
    })


def nueva_venta(request):
    if request.method != 'POST':
        return redirect('ventas:ventas_lista')

    form            = VentaForm(request.POST)
    producto_id     = request.POST.get('producto')
    presentacion_id = request.POST.get('presentacion')
    cantidad_raw    = request.POST.get('cantidad', '')
    precio_raw      = request.POST.get('precio_unitario', '')

    # ── Validar cantidad ───────────────────────────────────────────────────
    try:
        cantidad = int(cantidad_raw)
        if cantidad <= 0:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, "La cantidad debe ser un número entero mayor a 0.")
        return redirect('ventas:ventas_lista')

    # ── Validar precio ─────────────────────────────────────────────────────
    try:
        precio = Decimal(precio_raw)
        if precio < 0:
            raise ValueError
    except (InvalidOperation, ValueError, TypeError):
        messages.error(request, "El precio no es válido.")
        return redirect('ventas:ventas_lista')

    # ── Obtener producto ───────────────────────────────────────────────────
    try:
        producto = Producto.objects.prefetch_related('presentaciones').get(pk=producto_id)
    except Producto.DoesNotExist:
        messages.error(request, "Producto no encontrado.")
        return redirect('ventas:ventas_lista')

    # ── Verificar stock y obtener presentación ─────────────────────────────
    presentacion = None

    if presentacion_id:
        try:
            presentacion = PresentacionProducto.objects.get(pk=presentacion_id, producto=producto)
        except PresentacionProducto.DoesNotExist:
            messages.error(request, "Presentación no válida para este producto.")
            return redirect('ventas:ventas_lista')

        if cantidad > presentacion.cantidad:
            messages.error(
                request,
                f"Stock insuficiente. Solo hay {presentacion.cantidad} "
                f"'{presentacion.nombre}' de {producto.nombre}."
            )
            return redirect('ventas:ventas_lista')
    else:
        if cantidad > producto.cantidad_disponible:
            messages.error(
                request,
                f"Stock insuficiente. Solo hay {producto.cantidad_disponible} "
                f"unidades sueltas de {producto.nombre}."
            )
            return redirect('ventas:ventas_lista')

    # ── Guardar venta ──────────────────────────────────────────────────────
    if not form.is_valid():
        messages.error(request, "Revisa los campos del formulario.")
        return redirect('ventas:ventas_lista')

    venta = form.save()

    DetalleVenta.objects.create(
        venta=venta,
        producto=producto,
        presentacion=presentacion,
        cantidad=cantidad,
        precio_unitario=precio,
    )

    # ── Descontar stock ────────────────────────────────────────────────────
    if presentacion:
        presentacion.cantidad -= cantidad
        presentacion.save()
        unidades_descontadas = cantidad * presentacion.unidades
        desc = f"'{presentacion.nombre}'"
    else:
        producto.cantidad_disponible -= cantidad
        producto.save()
        unidades_descontadas = cantidad
        desc = "unidades sueltas"

    # ── Registrar movimiento de salida ─────────────────────────────────────
    Inventario.objects.create(
        producto=producto,
        tipo='salida',
        cantidad=unidades_descontadas,
        motivo='Venta registrada',
        ubicacion='Venta',
    )

    messages.success(request, f"Venta registrada: {cantidad} {desc} de {producto.nombre}.")
    return redirect('ventas:ventas_lista')


def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    if request.method == 'POST':
        for det in venta.detalles.all():
            if det.presentacion:
                det.presentacion.cantidad += det.cantidad
                det.presentacion.save()
                unidades = det.cantidad * det.presentacion.unidades
            else:
                det.producto.cantidad_disponible += det.cantidad
                det.producto.save()
                unidades = det.cantidad

            # Registrar devolución al inventario
            Inventario.objects.create(
                producto=det.producto,
                tipo='entrada',
                cantidad=unidades,
                motivo='Anulación de venta',
                ubicacion='Devolución',
            )

        venta.delete()
        messages.success(request, "Venta eliminada y stock restaurado.")
    return redirect('ventas:ventas_lista')


def producto_stock_json(request, pk):
    producto = get_object_or_404(
        Producto.objects.prefetch_related('presentaciones'), pk=pk
    )
    presentaciones = [
        {
            'id':       p.id,
            'nombre':   p.nombre,
            'unidades': p.unidades,
            'cantidad': p.cantidad,
            'precio':   float(p.precio),
        }
        for p in producto.presentaciones.all()
    ]
    return JsonResponse({
        'stock':          producto.cantidad_disponible,
        'precio':         float(producto.precio_unitario),
        'unidad':         producto.unidad,
        'presentaciones': presentaciones,
    })