from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm
from producto.models import Producto, Inventario, Categoria, PresentacionProducto


def ventas_lista(request):
    ventas = Venta.objects.prefetch_related(
        'detalles__producto',
        'detalles__presentacion'
    ).all().order_by('-fecha')
    form = VentaForm()
    detalle = DetalleVentaForm()
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

    form = VentaForm(request.POST)
    producto_ids     = request.POST.getlist('producto_id[]')
    presentacion_ids = request.POST.getlist('presentacion_id[]')
    cantidades       = request.POST.getlist('cantidad[]')
    precios          = request.POST.getlist('precio[]')

    def to_decimal(key, default='0'):
        try:
            return Decimal(request.POST.get(key, default) or default)
        except (InvalidOperation, TypeError):
            return Decimal('0')

    descuento_pct      = to_decimal('descuento_porcentaje')
    pago_efectivo      = to_decimal('pago_efectivo')
    pago_tarjeta       = to_decimal('pago_tarjeta')
    pago_transferencia = to_decimal('pago_transferencia')
    pago_nequi         = to_decimal('pago_nequi')
    pago_daviplata     = to_decimal('pago_daviplata')

    if not producto_ids:
        messages.error(request, "El carrito está vacío.")
        return redirect('ventas:ventas_lista')

    if not form.is_valid():
        messages.error(request, "Revisa los campos del formulario.")
        return redirect('ventas:ventas_lista')

    items_validados = []
    subtotal_venta  = Decimal('0')

    for i, prod_id in enumerate(producto_ids):
        try:
            cantidad = int(cantidades[i])
            precio   = Decimal(precios[i])
            if cantidad <= 0 or precio < 0:
                raise ValueError
        except (ValueError, TypeError, InvalidOperation, IndexError):
            messages.error(request, f"Datos inválidos en el ítem {i+1}.")
            return redirect('ventas:ventas_lista')

        try:
            producto = Producto.objects.prefetch_related('presentaciones').get(pk=prod_id)
        except Producto.DoesNotExist:
            messages.error(request, f"Producto {i+1} no encontrado.")
            return redirect('ventas:ventas_lista')

        pres_id      = presentacion_ids[i] if i < len(presentacion_ids) else ''
        presentacion = None

        if pres_id:
            try:
                presentacion = PresentacionProducto.objects.get(pk=pres_id, producto=producto)
            except PresentacionProducto.DoesNotExist:
                messages.error(request, f"Presentación inválida para {producto.nombre}.")
                return redirect('ventas:ventas_lista')

            if cantidad > presentacion.cantidad:
                messages.error(request, f"Stock insuficiente: solo hay {presentacion.cantidad} '{presentacion.nombre}' de {producto.nombre}.")
                return redirect('ventas:ventas_lista')
        else:
            if cantidad > producto.cantidad_disponible:
                messages.error(request, f"Stock insuficiente: solo hay {producto.cantidad_disponible} unidades de {producto.nombre}.")
                return redirect('ventas:ventas_lista')

        items_validados.append({
            'producto': producto, 'presentacion': presentacion,
            'cantidad': cantidad, 'precio': precio,
        })
        subtotal_venta += precio * cantidad

    monto_descuento = (subtotal_venta * descuento_pct) / Decimal('100')
    total_final     = subtotal_venta - monto_descuento

    # Validar que los pagos cubran el total
    total_pagado = pago_efectivo + pago_tarjeta + pago_transferencia + pago_nequi + pago_daviplata
    if total_pagado < total_final:
        messages.error(request, f"El total pagado (${total_pagado:,.0f}) no cubre el total de la venta (${total_final:,.0f}).".replace(',', '.'))
        return redirect('ventas:ventas_lista')

    venta = form.save(commit=False)
    venta.descuento_porcentaje = descuento_pct
    venta.total_con_descuento  = total_final
    venta.pago_efectivo        = pago_efectivo
    venta.pago_tarjeta         = pago_tarjeta
    venta.pago_transferencia   = pago_transferencia
    venta.pago_nequi           = pago_nequi
    venta.pago_daviplata       = pago_daviplata
    venta.save()

    for item in items_validados:
        producto     = item['producto']
        presentacion = item['presentacion']
        cantidad     = item['cantidad']
        precio       = item['precio']

        DetalleVenta.objects.create(
            venta=venta, producto=producto, presentacion=presentacion,
            cantidad=cantidad, precio_unitario=precio,
        )

        if presentacion:
            presentacion.cantidad -= cantidad
            presentacion.save()
            unidades = cantidad * presentacion.unidades
        else:
            producto.cantidad_disponible -= cantidad
            producto.save()
            unidades = cantidad

        Inventario.objects.create(
            producto=producto, tipo='salida', cantidad=unidades,
            motivo='Venta registrada', ubicacion='Venta',
        )

    messages.success(request, f"Venta registrada — Total: ${total_final:,.0f}".replace(',', '.'))
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

            Inventario.objects.create(
                producto=det.producto, tipo='entrada', cantidad=unidades,
                motivo='Anulación de venta', ubicacion='Devolución',
            )

        venta.delete()
        messages.success(request, "Venta eliminada y stock restaurado.")
    return redirect('ventas:ventas_lista')


def producto_stock_json(request, pk):
    producto = get_object_or_404(Producto.objects.prefetch_related('presentaciones'), pk=pk)
    presentaciones = [
        {'id': p.id, 'nombre': p.nombre, 'unidades': p.unidades, 'cantidad': p.cantidad, 'precio': float(p.precio)}
        for p in producto.presentaciones.all()
    ]
    return JsonResponse({
        'stock': producto.cantidad_disponible, 'precio': float(producto.precio_unitario),
        'unidad': producto.unidad, 'presentaciones': presentaciones,
    })
    # ─────────────────────────────────────────────
# Agrega estas vistas en ventas/views.py
# ─────────────────────────────────────────────

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from .models import Venta, Devolucion, DetalleDevolucion


def lista_devoluciones(request):
    """Página principal de devoluciones con historial."""
    devoluciones = Devolucion.objects.select_related('venta').prefetch_related('detalles__producto', 'detalles__presentacion')
    return render(request, 'ventas/devoluciones.html', {
        'devoluciones': devoluciones,
    })


def buscar_venta_devolucion(request):
    """
    AJAX: busca ventas por cliente o ID para iniciar una devolución.
    GET ?q=texto
    """
    q = request.GET.get('q', '').strip()
    if not q:
        return JsonResponse({'ventas': []})

    ventas = Venta.objects.filter(cliente__icontains=q).order_by('-fecha')[:10]
    # También busca por ID si el query es numérico
    if q.isdigit():
        ventas = (Venta.objects.filter(pk=int(q)) | ventas).distinct()

    data = []
    for v in ventas:
        data.append({
            'id':      v.pk,
            'cliente': v.cliente,
            'fecha':   v.fecha.strftime('%d/%m/%Y %H:%M'),
            'total':   float(v.total_venta),
        })
    return JsonResponse({'ventas': data})


def detalle_venta_devolucion(request, venta_id):
    """
    AJAX: devuelve los detalles de una venta para mostrar en el formulario de devolución.
    GET /ventas/devoluciones/venta/<id>/detalle/
    """
    venta = get_object_or_404(Venta, pk=venta_id)
    detalles = []
    for d in venta.detalles.select_related('producto', 'presentacion').all():
        detalles.append({
            'detalle_id':   d.pk,
            'producto_id':  d.producto.pk,
            'producto':     d.producto.nombre,
            'presentacion_id': d.presentacion.pk if d.presentacion else None,
            'presentacion': d.presentacion.nombre if d.presentacion else '',
            'cantidad':     d.cantidad,
            'precio':       float(d.precio_unitario),
            'subtotal':     float(d.subtotal()),
        })
    return JsonResponse({
        'venta_id': venta.pk,
        'cliente':  venta.cliente,
        'fecha':    venta.fecha.strftime('%d/%m/%Y %H:%M'),
        'total':    float(venta.total_venta),
        'descuento': float(venta.descuento_porcentaje),
        'detalles': detalles,
    })


@transaction.atomic
def registrar_devolucion(request):
    """
    POST: procesa y guarda la devolución.
    Subtarea 1 — guarda la devolución
    Subtarea 2 — advierte si no hay comprobante (validado en frontend y aquí)
    Subtarea 3 — actualiza inventario si corresponde
    Subtarea 4 — redirige al comprobante generado
    """
    if request.method != 'POST':
        return redirect('ventas:lista_devoluciones')

    venta_id          = request.POST.get('venta_id')
    tiene_comprobante = request.POST.get('tiene_comprobante') == '1'
    restaurar_stock   = request.POST.get('restaurar_stock') == '1'
    motivo            = request.POST.get('motivo', 'otro')
    observaciones     = request.POST.get('observaciones', '')

    producto_ids      = request.POST.getlist('producto_id[]')
    presentacion_ids  = request.POST.getlist('presentacion_id[]')
    cantidades        = request.POST.getlist('cantidad[]')
    precios           = request.POST.getlist('precio[]')

    # ── Subtarea 2: validar comprobante ──────────────────────────────
    if not tiene_comprobante:
        # El frontend ya mostró la advertencia; si el cajero igualmente envió el form
        # con tiene_comprobante=0, rechazamos a nivel de servidor también.
        messages.warning(request, 'No se puede registrar la devolución sin comprobante de compra.')
        return redirect('ventas:lista_devoluciones')

    venta = get_object_or_404(Venta, pk=venta_id)

    # ── Subtarea 1: construir y guardar la devolución ─────────────────
    total_devuelto = sum(
        int(cantidades[i]) * float(precios[i])
        for i in range(len(producto_ids))
    )

    devolucion = Devolucion.objects.create(
        venta=venta,
        motivo=motivo,
        observaciones=observaciones,
        restaurar_stock=restaurar_stock,
        tiene_comprobante=tiene_comprobante,
        total_devuelto=total_devuelto,
    )

    for i in range(len(producto_ids)):
        from producto.models import Producto, PresentacionProducto
        producto     = get_object_or_404(Producto, pk=producto_ids[i])
        presentacion = None
        if presentacion_ids[i] and presentacion_ids[i] != 'null':
            presentacion = PresentacionProducto.objects.filter(pk=presentacion_ids[i]).first()

        cantidad = int(cantidades[i])
        precio   = float(precios[i])

        DetalleDevolucion.objects.create(
            devolucion=devolucion,
            producto=producto,
            presentacion=presentacion,
            cantidad=cantidad,
            precio_unitario=precio,
        )

        # ── Subtarea 3: actualizar inventario ─────────────────────────
        if restaurar_stock and presentacion:
            presentacion.cantidad += cantidad
            presentacion.save()

    # ── Subtarea 4: comprobante generado — redirige a la vista ────────
    messages.success(request, f'Devolución {devolucion.numero} registrada correctamente.')
    return redirect('ventas:comprobante_devolucion', pk=devolucion.pk)


def comprobante_devolucion(request, pk):
    """Muestra el comprobante imprimible de una devolución."""
    devolucion = get_object_or_404(
        Devolucion.objects.select_related('venta').prefetch_related(
            'detalles__producto', 'detalles__presentacion'
        ),
        pk=pk
    )
    return render(request, 'ventas/comprobante_devolucion.html', {
        'devolucion': devolucion,
    })