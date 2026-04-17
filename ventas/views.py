from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm
from producto.models import Producto, Inventario, Categoria, PresentacionProducto


def ventas_lista(request):
    ventas     = Venta.objects.prefetch_related(
        'detalles__producto',
        'detalles__presentacion'
    ).all().order_by('-fecha')
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

    form             = VentaForm(request.POST)
    producto_ids     = request.POST.getlist('producto_id[]')
    presentacion_ids = request.POST.getlist('presentacion_id[]')
    cantidades       = request.POST.getlist('cantidad[]')
    precios          = request.POST.getlist('precio[]')

    if not producto_ids:
        messages.error(request, "El carrito está vacío.")
        return redirect('ventas:ventas_lista')

    if not form.is_valid():
        messages.error(request, "Revisa los campos del formulario.")
        return redirect('ventas:ventas_lista')

    items_validados = []
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
                messages.error(
                    request,
                    f"Stock insuficiente: solo hay {presentacion.cantidad} "
                    f"'{presentacion.nombre}' de {producto.nombre}."
                )
                return redirect('ventas:ventas_lista')
        else:
            if cantidad > producto.cantidad_disponible:
                messages.error(
                    request,
                    f"Stock insuficiente: solo hay {producto.cantidad_disponible} "
                    f"unidades sueltas de {producto.nombre}."
                )
                return redirect('ventas:ventas_lista')

        items_validados.append({
            'producto':     producto,
            'presentacion': presentacion,
            'cantidad':     cantidad,
            'precio':       precio,
        })

    venta = form.save()

    for item in items_validados:
        producto     = item['producto']
        presentacion = item['presentacion']
        cantidad     = item['cantidad']
        precio       = item['precio']

        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            presentacion=presentacion,
            cantidad=cantidad,
            precio_unitario=precio,
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
            producto=producto,
            tipo='salida',
            cantidad=unidades,
            motivo='Venta registrada',
            ubicacion='Venta',
        )

    total = sum(i['cantidad'] * i['precio'] for i in items_validados)
    messages.success(
        request,
        f"Venta registrada: {len(items_validados)} producto(s) — "
        f"Total: ${total:,.0f}".replace(',', '.')
    )
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