from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from .models import Venta, DetalleVenta
from .forms import VentaForm, DetalleVentaForm
from producto.models import Producto, Inventario, Categoria


def ventas_lista(request):
    ventas     = Venta.objects.prefetch_related('detalles__producto').all()
    form       = VentaForm()
    detalle    = DetalleVentaForm()
    categorias = Categoria.objects.prefetch_related('productos').all()

    return render(request, 'ventas.html', {
        'ventas':     ventas,
        'form':       form,
        'detalle':    detalle,
        'categorias': categorias,
    })


def nueva_venta(request):
    if request.method == 'POST':
        form        = VentaForm(request.POST)
        producto_id = request.POST.get('producto')
        cantidad    = request.POST.get('cantidad')
        precio      = request.POST.get('precio_unitario')

        try:
            producto = Producto.objects.get(pk=producto_id)
            cantidad = int(cantidad)
            precio   = Decimal(precio)
        except Exception:
            messages.error(request, "Datos inválidos. Selecciona un producto e intenta de nuevo.")
            return redirect('ventas:ventas_lista')

        if form.is_valid():
            if cantidad > producto.cantidad_disponible:
                messages.error(request, f"Stock insuficiente. Solo hay {producto.cantidad_disponible} unidades de {producto.nombre}.")
                return redirect('ventas:ventas_lista')

            venta = form.save()

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio
            )

            producto.cantidad_disponible -= cantidad
            producto.save()

            # ← Aquí solo agregamos tipo y motivo
            Inventario.objects.create(
                producto=producto,
                tipo='salida',
                cantidad=cantidad,
                motivo='Venta registrada',
                ubicacion='Venta'
            )

            messages.success(request, f"Venta de {producto.nombre} registrada correctamente.")
            return redirect('ventas:ventas_lista')

        messages.error(request, "Revisa los campos del formulario.")
        return redirect('ventas:ventas_lista')

    return redirect('ventas:ventas_lista')


def eliminar_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    for det in venta.detalles.all():
        det.producto.cantidad_disponible += det.cantidad
        det.producto.save()
    venta.delete()
    messages.success(request, "Venta eliminada y stock restaurado.")
    return redirect('ventas:ventas_lista')


def producto_stock_json(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return JsonResponse({
        'stock':  producto.cantidad_disponible,
        'precio': float(producto.precio_unitario),
        'unidad': producto.unidad,
    })