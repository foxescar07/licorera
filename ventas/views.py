from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.template import loader  # 🔥 AGREGADO
from ventas.models import Venta, DetalleVenta # pyright: ignore[reportMissingImports]
from .forms import VentaForm, DetalleVentaForm
from producto.models import Producto, Inventario


def ventas_lista(request):
    ventas   = Venta.objects.prefetch_related('detalles__producto').all()
    form     = VentaForm()
    detalle  = DetalleVentaForm()
    productos = Producto.objects.all()

   
    template = loader.get_template('ventas.html')

    return render(request, template.template.name, {
        'ventas':   ventas,
        'form':     form,
        'detalle':  detalle,
        'productos': productos,
    })


def nueva_venta(request):
    if request.method == 'POST':
        form    = VentaForm(request.POST)
        detalle = DetalleVentaForm(request.POST)

        if form.is_valid() and detalle.is_valid():
            producto = detalle.cleaned_data['producto']
            cantidad = detalle.cleaned_data['cantidad']

            if cantidad > producto.cantidad_disponible:
                messages.error(request, f"Stock insuficiente. Solo hay {producto.cantidad_disponible} unidades de {producto.nombre}.")
                return redirect('ventas:ventas_lista')

            venta = form.save()

            det = detalle.save(commit=False)
            det.venta = venta
            det.save()

            # Descontar stock
            producto.cantidad_disponible -= cantidad
            producto.save()

            # Registrar movimiento
            Inventario.objects.create(
                producto=producto,
                cantidad=-cantidad,
                ubicacion="Venta"
            )

            messages.success(request, f"Venta registrada correctamente.")
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
        'stock': producto.cantidad_disponible,
        'precio': float(producto.precio_unitario),
        'unidad': producto.unidad,
    })